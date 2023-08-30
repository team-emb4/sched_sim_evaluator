import sys
import os
import yaml
import matplotlib.pyplot as plt

from libs import util


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


# カスタムタグのコンストラクタ
def custom_constructor_schedulable(loader, node):
    data = loader.construct_mapping(node, deep=True)
    return SchedulableTag(**data)


def custom_constructor_unschedulable(loader, node):
    data = loader.construct_mapping(node, deep=True)
    return UnschedulableTag(**data)


# カスタムタグを登録
yaml.SafeLoader.add_constructor("!Schedulable", custom_constructor_schedulable)
yaml.SafeLoader.add_constructor("!Unschedulable", custom_constructor_unschedulable)


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

    # 入力ディレクトリの中にあるディレクトリの数をカウント
    log_dir_count = len(os.listdir(root_log_dir_path))

    # カウント結果を格納する配列を初期化
    max_utilization = [0] * log_dir_count
    yaml_count = [0] * log_dir_count
    schedulable_count = [0] * log_dir_count
    unschedulable_count = [0] * log_dir_count

    dir_list = os.listdir(root_log_dir_path)
    dir_list.sort()

    # 入力ディレクトリの中にあるディレクトリごとに処理
    for i, log_dir in enumerate(dir_list):
        # ディレクトリ名から数値を抽出
        number = util.extract_numbers_from_string(log_dir)
        if number is None:
            continue
        max_utilization[i] = number

        # ディレクトリ内のファイルを取得
        log_dir = os.path.join(root_log_dir_path, log_dir)
        log_file_list = os.listdir(log_dir)

        for file_name in log_file_list:
            # ファイル名が".yaml"で終わる場合のみ処理
            if file_name.endswith(".yaml"):
                yaml_count[i] += 1
                log_file_path = os.path.join(log_dir, file_name)

                # ファイルからresultを確認
                log_data = read_yaml_file(log_file_path)
                # resultが!Schedulableの場合
                if isinstance(log_data["result"], SchedulableTag):
                    schedulable_count[i] += 1
                # resultが!Unschedulableの場合
                elif isinstance(log_data["result"], UnschedulableTag):
                    unschedulable_count[i] += 1
                else:
                    print("Unknown Result")

    # カウント結果を表示
    accept = [0.0] * log_dir_count
    for i, subdir in enumerate(dir_list):
        print("Directory: {}".format(subdir))
        print("  Max utilization: {}".format(max_utilization[i]))
        print("  Number of .yaml files: {}".format(yaml_count[i]))
        print("  Number of schedulable: {}".format(schedulable_count[i]))
        print("  Number of unschedulable: {}".format(unschedulable_count[i]))
        accept[i] = schedulable_count[i] / yaml_count[i]
        print("  Acceptance of schedulable: {}".format(accept[i]))
        print("")

    # 全体の結果を表示
    print("Total:")
    print("  Number of .yaml files: {}".format(sum(yaml_count)))
    print("  Number of schedulable: {}".format(sum(schedulable_count)))
    print("  Number of unschedulable: {}".format(sum(unschedulable_count)))
    print("  Acceptance of schedulable: {}".format(sum(schedulable_count) / sum(yaml_count)))
    print("")

    # グラフを作成
    # ディレクトリ名からコア数を取得
    core = os.path.basename(root_log_dir_path)

    # アルゴリズムのディレクトリパスを取得
    algorithm_dir = os.path.dirname(os.path.dirname(root_log_dir_path))

    # アルゴリズムのディレクトリ名を取得
    algorithm_name = os.path.basename(algorithm_dir)

    # 縦軸: Acceptance of schedulable
    # 横軸: Max utilization
    plt.plot(max_utilization, accept, marker="o", color="blue", linestyle="-")
    plt.xlabel("Max utilization")
    plt.ylabel("Acceptance of schedulable")

    # グラフの保存先ディレクトリを作成
    os.makedirs(f"{algorithm_dir}/OutputsResult", exist_ok=True)

    # グラフを保存
    plt.savefig(f"{algorithm_dir}/OutputsResult/plot_accept_{algorithm_name}_{core}.png")

    # グラフを表示
    plt.show()


if __name__ == "__main__":
    # コマンドライン引数からディレクトリのパスを取得
    if len(sys.argv) != 2:
        print("Usage: python result_check.py /path/to/your/directory")
        sys.exit(1)

    input_directory = sys.argv[1]
    count_results(input_directory)
