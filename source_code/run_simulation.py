import argparse
import sys
import os
import re


def option_parser(args):
    parser = argparse.ArgumentParser()
    # DAGファイルの生成場所のパス
    parser.add_argument(
        "-d", "--create_dags", required=True, type=str, help="path to create DAGs."
    )
    # シミュレータ実行場所のパス
    parser.add_argument("-s", "--simulator", required=True, type=str, help="path to simulator.")
    # シミュレータ実行時のコア数
    parser.add_argument("-c", "--core_num", required=True, type=int, help="number of cores.")
    args = parser.parse_args()

    return vars(args)


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


if __name__ == "__main__":
    # 引数をパース
    args = option_parser(sys.argv[1:])

    # simulatorディレクトリのパスを取得
    simulator_dir_path = os.path.abspath("../")

    # アルゴリズム名を取得
    algorithm = os.path.basename(os.path.dirname(args["simulator"]))
    print("algorithm: " + algorithm)

    # DAGファイルの準備
    # すでにDAGファイルが生成されている場合はスキップ
    if not os.path.exists(f"{algorithm}/"):
        # DAGファイルを生成
        print("----------Create DAGs----------")
        # configファイルを取得
        config_dir_path = os.path.abspath("../config")
        config_files = os.listdir("../config")
        config_paths = [os.path.join(config_dir_path, file_name) for file_name in config_files]
        # ディレクトリ名から数値を抽出
        max_utilization = [0] * len(config_files)
        for i, file in enumerate(config_files):
            number = extract_numbers_from_string(file)
            if number is None:
                continue
            max_utilization[i] = number / 10

        if not os.path.exists("../DAGs"):
            os.mkdir("../DAGs")
        DAG_dir_path = os.path.abspath(args["create_dags"])
        os.chdir(DAG_dir_path)
        command_create_dags = (
            "python3 run_generator.py -c {config} "
            "-d {simulator_dir_path}/DAGs/Max_utilization-{utilization}"
        )
        for i, config in enumerate(config_paths):
            full_command = command_create_dags.format(
                config=config,
                simulator_dir_path=simulator_dir_path,
                utilization=max_utilization[i],
            )
            print(full_command)
            os.system(full_command)
        print("----------Finish----------")

        os.chdir(simulator_dir_path + "/source_code")

        # divide_files.pyを実行
        print("----------Divide files----------")
        FOLDER_NUM = 1000  # 分割後のフォルダ数
        if not os.path.exists(f"{algorithm}/"):
            os.mkdir(f"{algorithm}/")
        DAGs_dirs = os.listdir("../DAGs/")
        command_divide_files = (
            "python3 divide_files.py -s ../DAGs/{DAGs_dir}/DAGs/ -n {folder_num} "
            "-o {algorithm}/UsedDag/{DAGs_dir}/"
        )
        for DAGs_dir in DAGs_dirs:
            full_command = command_divide_files.format(
                DAGs_dir=DAGs_dir, folder_num=FOLDER_NUM, algorithm=algorithm
            )
            print(full_command)
            os.system(full_command)
        # configファイルをコピー
        command = "cp {config} {algorithm}/UsedDag/MAX_utilization-{utilization}/"
        for config in config_paths:
            full_command = command.format(
                config=config, algorithm=algorithm, utilization=max_utilization[i]
            )
            print(full_command)
            os.system(full_command)
        print("----------Finish----------")

    # all_execute.pyを実行
    print("----------All execute----------")
    execute_simulator_path = os.path.abspath(args["simulator"])
    core_num = args["core_num"]
    command_all_execute = (
        f"python3 all_execute.py -e {execute_simulator_path} -d {algorithm}/UsedDag/ -c {core_num}"
    )
    print(command_all_execute)
    os.system(command_all_execute)
    print("----------Finish----------")

    # result_check.pyを実行
    print("----------Result check----------")
    command_result_check = f"python3 result_check.py {algorithm}/SchedResult/{core_num}-cores/"
    print(command_result_check)
    os.system(command_result_check)
    print("----------Finish----------")
