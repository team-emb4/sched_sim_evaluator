import sys
import os
import yaml
import matplotlib.pyplot as plt

from libs import util
from libs.util import algo_list


# カスタムタグの定義
# !Schedulableタグの定義
class SchedulableTag:
    def __init__(self, high_dedicated_cores, low_dedicated_cores):
        self.high_dedicated_cores = high_dedicated_cores
        self.low_dedicated_cores = low_dedicated_cores


# !Unschedulableタグの定義
class UnschedulableTag:
    def __init__(self, reason, insufficient_cores):
        self.reason = reason
        self.insufficient_cores = insufficient_cores


# JobEventTimesタグの定義
class JobEventTimes:
    def __init__(self, time):
        self.time = time


# カスタムタグのコンストラクタ
def custom_constructor_schedulable(loader, node):
    data = loader.construct_mapping(node, deep=True)
    return SchedulableTag(**data)


def custom_constructor_unschedulable(loader, node):
    data = loader.construct_mapping(node, deep=True)
    return UnschedulableTag(**data)


def custom_constructor_job_event(loader, node):
    data = loader.construct_scalar(node)
    return JobEventTimes(int(data))


# カスタムタグを登録
yaml.SafeLoader.add_constructor("!Schedulable", custom_constructor_schedulable)
yaml.SafeLoader.add_constructor("!Unschedulable", custom_constructor_unschedulable)
yaml.SafeLoader.add_constructor("!StartTime", custom_constructor_job_event)
yaml.SafeLoader.add_constructor("!ResumeTime", custom_constructor_job_event)
yaml.SafeLoader.add_constructor("!FinishTime", custom_constructor_job_event)
yaml.SafeLoader.add_constructor("!PreemptedTime", custom_constructor_job_event)


# yamlファイルを読み込み
def read_yaml_file(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return data


# ディレクトリ内のファイルのうち、"result: !Schedulable"と"result: !Unschedulable"の数をカウント
def count_results(root_log_dir_path):
    # 入力ディレクトリの絶対パスを取得
    if not os.path.isabs(root_log_dir_path):
        root_log_dir_path = os.path.abspath(root_log_dir_path)

    # 入力ディレクトリパスのSchedResult以降を削除
    algorithm_dir = root_log_dir_path.split("/SchedResult")[0]

    # アルゴリズムのディレクトリ名を取得
    algorithm = os.path.basename(algorithm_dir)
    if algorithm not in algo_list:
        # 使用可能なアルゴリズム名を表示
        util.print_log(
            "Algorithm name is not correct. Available algorithm names are:", log_kind="ERROR"
        )
        for key in algo_list.keys():
            print(f"  {key}")
        exit(1)
    else:
        properties = algo_list[algorithm]  # アルゴリズムのプロパティを取得
        # 実行モードが2種類ある場合はノンプリエンプティブとプリエンプティブのどちらであるかを取得
        if properties["preemptive"] == "true":
            pre = os.path.basename(os.path.dirname(root_log_dir_path))
            util.print_log("algorithm: " + algorithm + "-" + pre)
        else:
            util.print_log("algorithm: " + algorithm)

    # 入力ディレクトリの中にあるディレクトリの数をカウント
    log_dir_count = len(os.listdir(root_log_dir_path))

    # カウント結果を格納する配列を初期化
    max_utilization = [0] * log_dir_count
    yaml_count = [0] * log_dir_count
    schedulable_count = [0] * log_dir_count
    unschedulable_count = [0] * log_dir_count
    true_count = [0] * log_dir_count
    false_count = [0] * log_dir_count

    dir_list = os.listdir(root_log_dir_path)
    dir_list.sort()

    # 入力ディレクトリの中にあるディレクトリごとに処理
    for i, log_dir in enumerate(dir_list):
        util.print_log("Target directory: " + log_dir)
        # ディレクトリ名から数値を抽出
        number = util.extract_numbers_from_string(log_dir)
        if number is None:
            continue
        max_utilization[i] = number

        # ディレクトリ内のファイルを取得
        log_dir = os.path.join(root_log_dir_path, log_dir)
        log_file_list = os.listdir(log_dir)

        for j, file_name in enumerate(log_file_list):
            # プログレスバーを表示
            util.progress_bar(j, len(log_file_list))

            # ファイル名が".yaml"で終わる場合のみ処理
            if file_name.endswith(".yaml"):
                yaml_count[i] += 1
                log_file_path = os.path.join(log_dir, file_name)

                # ファイルからresultを確認
                log_data = read_yaml_file(log_file_path)

                # resultがSchedulableまたはUnschedulableで表される場合
                if properties["result"] == "schedulability":
                    # resultが!Schedulableの場合
                    if isinstance(log_data["result"], SchedulableTag):
                        schedulable_count[i] += 1
                    # resultが!Unschedulableの場合
                    elif isinstance(log_data["result"], UnschedulableTag):
                        unschedulable_count[i] += 1
                    else:
                        print("Unknown Result")

                else:  # resultがtrueまたはfalseで表される場合
                    # resultがtrueの場合
                    if log_data["result"]:
                        true_count[i] += 1
                    # resultがfalseの場合
                    else:
                        false_count[i] += 1

        # プログレスバーを表示
        util.progress_bar(1, 1)
        print("")

    # カウント結果を表示
    print("==============Result==============")
    accept = [0.0] * log_dir_count
    for i, subdir in enumerate(dir_list):
        print(f"Directory: {subdir}")
        print(f"  Max utilization: {max_utilization[i]}")
        print(f"  Number of .yaml files: {yaml_count[i]}")
        if properties["result"] == "schedulability":
            print(f"  Number of schedulable: {schedulable_count[i]}")
            print(f"  Number of schedulable: {unschedulable_count[i]}")
            accept[i] = schedulable_count[i] / yaml_count[i]
            print(f"  Acceptance of schedulable: {accept[i]}")
        else:
            print(f"  Number of true: {true_count[i]}")
            print(f"  Number of false: {false_count[i]}")
            accept[i] = true_count[i] / yaml_count[i]
            print(f"  Acceptance of true: {accept[i]}")
        print("")

    # 全体の結果を表示
    print("Total:")
    print(f"  Number of directories: {sum(yaml_count)}")
    if properties["result"] == "schedulability":
        print(f"  Number of schedulable: {sum(schedulable_count)}")
        print(f"  Number of unschedulable: {sum(unschedulable_count)}")
        print(f"  Acceptance of schedulable: {sum(schedulable_count) / sum(yaml_count)}")
    else:
        print(f"  Number of true: {sum(true_count)}")
        print(f"  Number of false: {sum(false_count)}")
        print(f"  Acceptance of true: {sum(true_count) / sum(yaml_count)}")
    print("")
    print("==================================")
    # グラフを作成
    # ディレクトリ名からコア数を取得
    core = os.path.basename(root_log_dir_path)

    # グラフの初期化
    plt.figure()

    # 縦軸: Acceptance of schedulable(true)
    # 横軸: Max utilization
    plt.plot(max_utilization, accept, marker="o", color="blue", linestyle="-")
    plt.xlabel("Max utilization")
    if properties["result"] == "schedulability":
        plt.ylabel("Acceptance of schedulable")
    else:
        plt.ylabel("Acceptance of true")

    # グラフの保存先ディレクトリを作成
    os.makedirs(f"{algorithm_dir}/OutputsResult", exist_ok=True)

    # グラフを保存
    if properties["preemptive"] == "true":
        plt.savefig(
            f"{algorithm_dir}/OutputsResult/plot_accept_{algorithm}_{pre}_{core}-cores.png"
        )
    else:
        plt.savefig(f"{algorithm_dir}/OutputsResult/plot_accept_{algorithm}_{core}-cores.png")

    # グラフを表示
    plt.show()


if __name__ == "__main__":
    # コマンドライン引数からディレクトリのパスを取得
    if len(sys.argv) != 2:
        print("Usage: python result_check.py /path/to/your/directory")
        sys.exit(1)

    input_directory = sys.argv[1]
    count_results(input_directory)
