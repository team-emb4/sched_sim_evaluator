import argparse
import sys
import os

from libs import util
from libs.util import algorithm_list
from libs import divide_files
from libs import batch_simulation
from libs import result_check


def option_parser(args):
    parser = argparse.ArgumentParser()
    # DAGファイル生成アルゴリズム RD-Genの実行フォルダパス(すでにDAGファイルが生成されている場合は指定しなくても良い)
    parser.add_argument(
        "-d", "--dag_creator", required=False, type=str, help="path to dag creator."
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

    # evaluatorディレクトリのパスを取得
    evaluator_dir_path = os.path.abspath("../")

    # アルゴリズム名を取得
    algorithm = os.path.basename(os.path.dirname(args["simulator"]))
    if algorithm not in algorithm_list:
        print("Algorithm name is not correct.")
        exit(1)
    else:
        properties = algorithm_list[algorithm]  # アルゴリズムのプロパティを取得
        print("algorithm: " + algorithm)

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

    # DAGファイルの準備
    # DAGsフォルダがすでに存在する場合はスキップ
    if os.path.exists(f"{evaluator_dir_path}/DAGs/"):
        print("----------DAGs folder already exists----------")
    else:
        # DAGファイルを生成
        print("----------Create DAGs----------")
        # RD-Genの実行パスが指定されていない場合はエラー
        if args["dag_creator"] is None:
            print("Please specify the path to DAG creator.")
            exit(1)

        if not os.path.exists("../DAGs"):
            os.mkdir("../DAGs")
        DAG_creator_path = os.path.abspath(args["dag_creator"])
        os.chdir(DAG_creator_path)
        command_create_dags = (
            "python3 run_generator.py -c {config} "
            "-d {simulator_dir_path}/DAGs/Max_utilization-{utilization}"
        )
        for i, config in enumerate(config_paths):
            full_command = command_create_dags.format(
                config=config,
                simulator_dir_path=evaluator_dir_path,
                utilization=max_utilization[i],
            )
            print(full_command)
            os.system(full_command)
        print("----------Finish----------")

    os.chdir(evaluator_dir_path + "/source_code")

    # UsedDagフォルダの準備
    # UsedDagフォルダがすでに存在する場合はスキップ
    if os.path.exists(f"{algorithm}/UsedDag/"):
        print("----------UsedDag folder already exists----------")
    else:
        print("----------Prepare UsedDag folder----------")
        if not os.path.exists(f"{algorithm}/"):
            os.mkdir(f"{algorithm}/")
        DAGs_dirs = os.listdir("../DAGs/")
        # 入力DAGの形式がファイルの場合はDAGファイルをそのまま配置
        if properties["input_DAG"] == "file":
            os.mkdir(f"{algorithm}/UsedDag/")
            command = "cp -r ../DAGs/{DAGs_dir}/DAGs/ {algorithm}/UsedDag/{DAGs_dir}"
            for DAGs_dir in DAGs_dirs:
                full_command = command.format(
                    DAGs_dir=DAGs_dir,
                    algorithm=algorithm,
                )
                print(full_command)
                os.system(full_command)
        else:  # 入力DAGの形式がフォルダの場合はファイルを分割して配置
            # divide_files.pyを実行
            print("----------Divide files----------")
            FOLDER_NUM = 1000  # 分割後のフォルダ数
            DAGs_dirs = os.listdir("../DAGs/")
            for DAGs_dir in DAGs_dirs:
                divide_files.divide_files_to_folders(
                    source_folder=f"../DAGs/{DAGs_dir}/DAGs/",
                    num_folders=FOLDER_NUM,
                    output_folder_path=f"{algorithm}/UsedDag/{DAGs_dir}/",
                )
            print("----------Finish----------")

        # configファイルをコピー
        command = (
            "cp {config} "
            "{evaluator_dir_path}/source_code/{algorithm}/UsedDag/Max_utilization-{utilization}/"
        )
        for i, config in enumerate(config_paths):
            full_command = command.format(
                config=config,
                evaluator_dir_path=evaluator_dir_path,
                algorithm=algorithm,
                utilization=max_utilization[i],
            )
            print(full_command)
            os.system(full_command)
        print("----------Finish----------")

    # batch_simulation.pyを実行
    print("----------Batch simulation----------")
    execute_simulator_path = os.path.abspath(args["simulator"])
    core_num = args["core_num"]
    batch_simulation.execute_command_in_subdirectories(
        execute_dir=execute_simulator_path,
        dagsets_root_dir=f"{algorithm}/UsedDag/",
        core_num=core_num,
    )
    os.chdir(evaluator_dir_path + "/source_code")
    print("----------Finish----------")

    # result_check.pyを実行
    print("----------Result check----------")
    # 実行モードが2種類ある場合はノンプリエンプティブとプリエンプティブの結果をそれぞれカウント
    if properties["execution_mode"] == "two":
        print("----------NonPreemptive----------")
        result_check.count_results(f"{algorithm}/SchedResult/NonPreemptive/{core_num}-cores/")
        print("----------Preemptive----------")
        result_check.count_results(f"{algorithm}/SchedResult/Preemptive/{core_num}-cores/")
    else:
        result_check.count_results(f"{algorithm}/SchedResult/{core_num}-cores/")
    print("----------Finish----------")
