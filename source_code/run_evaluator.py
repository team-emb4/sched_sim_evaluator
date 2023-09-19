import argparse
import sys
import os

from libs import util
from libs.util import algo_list
from libs import divide_files
from libs import batch_simulation
from libs import result_check


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dag_creator", required=False, type=str, help="path to RD-Gen.")
    parser.add_argument("-s", "--simulator", required=True, type=str, help="path to simulator.")
    parser.add_argument("-c", "--core_num", required=True, type=int, help="number of cores.")
    args = parser.parse_args()

    return vars(args)


if __name__ == "__main__":
    start_time = util.print_log("==============Start run_evaluator.py==============")
    args = option_parser(sys.argv[1:])
    evaluator_dir_path = os.path.abspath("../")

    algo_name = os.path.basename(os.path.dirname(args["simulator"]))
    if algo_name not in algo_list:
        util.print_log(
            "Algorithm name is not correct. Available algorithm names are:", log_kind="ERROR"
        )
        for key in algo_list.keys():
            print(f"  {key}")
        exit(1)
    else:
        algo_properties = algo_list[algo_name]
        util.print_log("Target algorithm: " + algo_name)

    # config下の各ファイル名から利用率(数値)を抽出
    config_dir_path = os.path.abspath("../config")
    config_files = os.listdir("../config")
    config_paths = [os.path.join(config_dir_path, file_name) for file_name in config_files]
    max_utilization = [0] * len(config_files)
    for i, file in enumerate(config_files):
        number = util.extract_numbers_from_string(file)
        if number is None:
            continue
        max_utilization[i] = number / 10

    util.print_log("==============Generate DAG==============")
    if os.path.exists(f"{evaluator_dir_path}/DAGs/"):
        util.print_log("DAGs already exists. Skip generate DAG.")
    else:
        if args["dag_creator"] is None:
            util.print_log(
                "DAG creator path is not specified. Please specify it with the -d option.",
                log_kind="ERROR",
            )
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

    os.chdir(evaluator_dir_path + "/source_code")

    util.print_log("==============Prepare UsedDag==============")
    if os.path.exists(f"{algo_name}/UsedDag/"):
        util.print_log("UsedDag already exists. Skip prepare UsedDag.")
    else:
        if not os.path.exists(f"{algo_name}/"):
            os.mkdir(f"{algo_name}/")
        DAGs_dirs = os.listdir("../DAGs/")

        if algo_properties["input_DAG"] == "file":  # 入力DAGの形式がファイルの場合はDAGファイルをそのまま配置
            os.mkdir(f"{algo_name}/UsedDag/")
            command = "cp -r ../DAGs/{DAGs_dir}/DAGs/ {algorithm}/UsedDag/{DAGs_dir}"
            for DAGs_dir in DAGs_dirs:
                full_command = command.format(
                    DAGs_dir=DAGs_dir,
                    algorithm=algo_name,
                )
                os.system(full_command)
        else:  # 入力DAGの形式がフォルダの場合はファイルを分割して配置
            util.print_log("Divide files")
            FOLDER_NUM = 1000  # 分割後のフォルダ数
            DAGs_dirs = os.listdir("../DAGs/")
            for DAGs_dir in DAGs_dirs:
                divide_files.divide_files_to_folders(
                    source_folder=f"../DAGs/{DAGs_dir}/DAGs/",
                    num_folders=FOLDER_NUM,
                    output_folder_path=f"{algo_name}/UsedDag/{DAGs_dir}/",
                )

        command = (
            "cp {config} "
            "{evaluator_dir_path}/source_code/{algorithm}/UsedDag/Max_utilization-{utilization}/"
        )
        for i, config in enumerate(config_paths):
            full_command = command.format(
                config=config,
                evaluator_dir_path=evaluator_dir_path,
                algorithm=algo_name,
                utilization=max_utilization[i],
            )
            os.system(full_command)

    util.print_log("==============Batch simulation==============")
    execute_simulator_path = os.path.abspath(args["simulator"])
    core_num = args["core_num"]
    batch_simulation.execute_command_in_subdirectories(
        execute_dir=execute_simulator_path,
        dagsets_root_dir=f"{algo_name}/UsedDag/",
        core_num=core_num,
    )
    os.chdir(evaluator_dir_path + "/source_code")

    util.print_log("==============Result check==============")
    if algo_properties["execution_mode"] == "two":
        result_check.count_results(f"{algo_name}/SchedResult/NonPreemptive/{core_num}-cores/")
        result_check.count_results(f"{algo_name}/SchedResult/Preemptive/{core_num}-cores/")
    else:
        result_check.count_results(f"{algo_name}/SchedResult/{core_num}-cores/")

    util.print_log("==============End run_evaluator.py==============")
    util.print_log("Evaluation time: ", start_time=start_time)
