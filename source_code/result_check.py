import sys
import os
import yaml
import re
import matplotlib.pyplot as plt


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


# 文字列から数値を抽出
def extract_numbers_from_string(input_string):
    # 正規表現パターン: 数字の連続した部分を抽出
    pattern = r"\d+(\.\d+)?"

    # 正規表現にマッチする部分を取得
    match = re.search(pattern, input_string)

    # マッチした部分を数値に変換して返す
    if match:
        number = float(match.group())
        return number
    else:
        return None


# yamlファイルを読み込み
def read_yaml_file(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return data


# ディレクトリ内のファイルのうち、"result: !Schedulable"と"result: !Unschedulable"の数をカウント
def count_results(directory_path):
    # 入力ディレクトリの絶対パスを取得
    if not os.path.isabs(directory_path):
        directory_path = os.path.abspath(directory_path)

    # 入力ディレクトリの中にあるディレクトリの数をカウント
    subdir_count = len(os.listdir(directory_path))

    # カウント結果を格納する配列を初期化
    max_utilization = [0] * subdir_count
    yaml_count = [0] * subdir_count
    schedulable_count = [0] * subdir_count
    unschedulable_count = [0] * subdir_count

    dir_list = os.listdir(directory_path)
    dir_list.sort()

    # 入力ディレクトリの中にあるディレクトリごとに処理
    for i, subdir in enumerate(dir_list):
        # ディレクトリ名から数値を抽出
        number = extract_numbers_from_string(subdir)
        if number is None:
            continue
        max_utilization[i] = number

        # ディレクトリ内のファイルを取得
        subdir = os.path.join(directory_path, subdir)
        file_list = os.listdir(subdir)

        for file_name in file_list:
            # ファイル名が".yaml"で終わる場合のみ処理
            if file_name.endswith(".yaml"):
                yaml_count[i] += 1
                file_path = os.path.join(subdir, file_name)

                # ファイルからresultを確認
                data = read_yaml_file(file_path)
                # resultが!Schedulableの場合
                if isinstance(data["result"], SchedulableTag):
                    schedulable_count[i] += 1
                # resultが!Unschedulableの場合
                elif isinstance(data["result"], UnschedulableTag):
                    unschedulable_count[i] += 1
                else:
                    print("Unknown Result")

    # カウント結果を表示
    accept = [0.0] * subdir_count
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
    core = os.path.basename(directory_path)

    # アルゴリズムのディレクトリパスを取得
    algorithm_dir = os.path.dirname(os.path.dirname(directory_path))

    # アルゴリズムのディレクトリ名を取得
    algorithm_name = os.path.basename(algorithm_dir)

    # print(max_utilization)
    # print(accept)

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
