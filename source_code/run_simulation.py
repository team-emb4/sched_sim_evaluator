import argparse
import sys
import os

from lib import util
from lib import divide_files
from lib import all_execute
from lib import result_check


def option_parser(args):
    parser = argparse.ArgumentParser()
    # DAGファイル生成アルゴリズム RD-Genの実行フォルダパス
    parser.add_argument(
        "-d", "--create_dags", required=True, type=str, help="path to create DAGs."
    )
    # シミュレータ実行場所のパス
    parser.add_argument("-s", "--simulator", required=True, type=str, help="path to simulator.")
    # シミュレータ実行時のコア数
    parser.add_argument("-c", "--core_num", required=True, type=int, help="number of cores.")
    args = parser.parse_args()

    return vars(args)


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
        # config下の各ファイル名から数値を抽出
        config_dir_path = os.path.abspath("../config")
        config_files = os.listdir("../config")
        config_paths = [os.path.join(config_dir_path, file_name) for file_name in config_files]
        # ディレクトリ名から数値を抽出
        max_utilization = [0] * len(config_files)
        for i, file in enumerate(config_files):
            number = util.extract_numbers_from_string(file)
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
        for DAGs_dir in DAGs_dirs:
            divide_files.divide_files_to_folders(
                source_folder=f"../DAGs/{DAGs_dir}/DAGs/",
                num_folders=FOLDER_NUM,
                output_folder_path=f"{algorithm}/UsedDag/{DAGs_dir}/",
            )
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
    all_execute.execute_command_in_subdirectories(
        execute_dir=execute_simulator_path, root_dir=f"{algorithm}/UsedDag/", core_num=core_num
    )
    os.chdir(simulator_dir_path + "/source_code")
    print("----------Finish----------")

    # result_check.pyを実行
    print("----------Result check----------")
    result_check.count_results(f"{algorithm}/SchedResult/{core_num}-cores/")
    print("----------Finish----------")
