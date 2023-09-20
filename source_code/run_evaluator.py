import argparse
import sys
import os

from libs import util
from libs.util import get_algorithm_properties
from libs import divide_files
from libs import batch_simulation
from libs import result_check


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--RD_Gen", required=False, type=str, help="path to RD-Gen.")
    parser.add_argument("-s", "--simulator", required=True, type=str, help="path to simulator.")
    parser.add_argument("-c", "--core_num", required=True, type=int, help="number of cores.")
    args = parser.parse_args()

    return vars(args)


if __name__ == "__main__":
    start_time = util.print_log("==============Start run_evaluator.py==============")
    args = option_parser(sys.argv[1:])
    algo_name = os.path.basename(os.path.dirname(args["simulator"]))
    algo_properties = get_algorithm_properties(algo_name)
    util.print_log("Target algorithm: " + algo_name)

    util.print_log("==============Generate DAG==============")
    config_path_list = [os.path.join(os.path.abspath("../config"), file_name)
                        for file_name in os.listdir("../config")]
    evaluator_path = os.path.abspath("../")
    if os.path.exists(f"{evaluator_path}/DAGs/"):
        util.print_log("DAGs already exists. Skip generate DAG.")
    else:
        if args["RD_Gen"] is None:
            util.print_log(
                "RD_Gen path is not specified. Please specify it with the -g option.",
                log_kind="ERROR",
            )
            exit(1)

        os.mkdir("../DAGs")
        os.chdir(os.path.abspath(args["RD_Gen"]))
        command_create_dags = (
            "python3 run_generator.py -c {config_path} "
            "-d {evaluator_path}/DAGs/Max_utilization-{utilization}"
        )
        for config_path in config_path_list:
            full_command = command_create_dags.format(
                config_path=config_path,
                evaluator_path=evaluator_path,
                utilization=(util.extract_utilization_from_name(os.path.basename(config_path))/10),
            )
            os.system(full_command)
    os.chdir(evaluator_path + "/source_code")

    util.print_log("==============Prepare UsedDag==============")
    if os.path.exists(f"{algo_name}/UsedDag/"):
        util.print_log("UsedDag already exists. Skip prepare UsedDag.")
    else:
        if not os.path.exists(f"{algo_name}/"):
            os.mkdir(f"{algo_name}/")
        DAGs_dir_list = os.listdir("../DAGs/")

        if algo_properties["input"] == "DAG":  # 入力がDAGの場合はDAGファイルをそのまま配置
            os.mkdir(f"{algo_name}/UsedDag/")
            util.print_log("Copy files")
            command = "cp -r ../DAGs/{DAGs_dir}/DAGs/ {algorithm}/UsedDag/{DAGs_dir}"
            for DAGs_dir in DAGs_dir_list:
                full_command = command.format(
                    DAGs_dir=DAGs_dir,
                    algorithm=algo_name,
                )
                os.system(full_command)
        else:  # 入力がDAGSetの場合はファイルを分割して配置
            util.print_log("Divide files")
            DIR_NUM = 1000  # 分割後のフォルダ数
            for DAGs_dir in DAGs_dir_list:
                divide_files.divide_dag_files_to_dirs(
                    input_dir_path=f"../DAGs/{DAGs_dir}/DAGs/",
                    num_dirs=DIR_NUM,
                    output_dir_path=f"{algo_name}/UsedDag/{DAGs_dir}/",
                )

        # configファイルをUsedDagにコピー
        command = (
            "cp {config} "
            "{evaluator_dir_path}/source_code/{algorithm}/UsedDag/Max_utilization-{utilization}/"
        )
        for config_path in config_path_list:
            full_command = command.format(
                config=config_path,
                evaluator_dir_path=evaluator_path,
                algorithm=algo_name,
                utilization=(util.extract_utilization_from_name(os.path.basename(config_path))/10)
            )
            os.system(full_command)

    util.print_log("==============Batch simulation==============")
    core_num = args["core_num"]
    batch_simulation.run_simulation_for_all_inputs(
        simulator_dir=os.path.abspath(args["simulator"]),
        root_input_tasks_dir=f"{algo_name}/UsedDag/",
        core_num=core_num,
    )
    os.chdir(evaluator_path + "/source_code")

    util.print_log("==============Result check==============")
    core_num = args["core_num"]
    if algo_properties["preemptive"] == "true":
        result_check.count_results(f"{algo_name}/SchedResult/NonPreemptive/{core_num}-cores/")
        result_check.count_results(f"{algo_name}/SchedResult/Preemptive/{core_num}-cores/")
    else:
        result_check.count_results(f"{algo_name}/SchedResult/{core_num}-cores/")

    util.print_log("==============End run_evaluator.py==============")
    util.print_log("Evaluation time: ", start_time=start_time)
