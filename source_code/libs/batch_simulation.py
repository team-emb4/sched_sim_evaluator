import os
import sys
import argparse
import datetime

from libs import util
from libs.util import get_algorithm_properties


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--execute_dir", required=True, type=str, help="path to execute directory."
    )
    parser.add_argument(
        "-d",
        "--input_dag_group_dir",
        required=True,
        type=str,
        help="path to input dag group directory.",
    )
    parser.add_argument("-c", "--core", required=True, type=int, help="number of cores")
    args = parser.parse_args()

    return vars(args)


# 入力されたディレクトリ内のすべてのサブディレクトリに対してコマンドを実行
def execute_command_in_subdirectories(execute_dir, dagsets_root_dir, core_num):
    now = datetime.datetime.now()
    seconds = now.strftime("%Y-%m-%d-%H-%M-%S")
    current_dir = os.getcwd()
    if not os.path.isabs(dagsets_root_dir):
        dagsets_root_dir = os.path.abspath(dagsets_root_dir)

    os.chdir(execute_dir)
    algo_name = os.path.basename(os.getcwd())
    algo_properties = get_algorithm_properties(algo_name)
    util.print_log("Target algorithm: " + algo_name)

    output_root_dir = f"{current_dir}/{algo_name}/SchedResult/{core_num}-cores"
    match algo_properties:
        case {"input": "DAGSet", "preemptive": "false"}:
            command = "cargo run -- -d {input} -c {core} -o {output_dir}"
        case {"input": "DAGSet", "preemptive": "true"}:
            command = "cargo run -- -d {input} -c {core} -o {output_dir} {preempt}"
            nonpre_output_root_dir = (
                f"{current_dir}/{algo_name}/SchedResult/NonPreemptive/{core_num}-cores"
            )
            preempt_output_root_dir = (
                f"{current_dir}/{algo_name}/SchedResult/Preemptive/{core_num}-cores"
            )
        case {"input": "DAG", "preemptive": "false"}:
            command = "cargo run -- -f {input} -c {core} -o {output_dir}"
        case _:
            util.print_log("Algorithm properties are not correct.", log_kind="ERROR")
            exit(1)

    util.print_log(f"Core number: {core_num}")

    if (algo_properties["preemptive"] == "true" and os.path.exists(nonpre_output_root_dir)) or (
        algo_properties["preemptive"] == "false" and os.path.exists(output_root_dir)
    ):
        util.print_log(f"Simulation results for {core_num}-core are already exists.")
        util.print_log("Do you want to continue and delete the existing results? (y/n)")
        answer = input()
        if answer == "y" or answer == "Y":
            util.print_log("Deleted the existing results")
            if algo_properties["preemptive"] == "true":
                os.system(f"rm -rf {nonpre_output_root_dir}")
                os.system(f"rm -rf {preempt_output_root_dir}")
            else:
                os.system(f"rm -rf {output_root_dir}")
        else:
            util.print_log("Exit.")
            exit(1)

    log_dir = f"{current_dir}/{algo_name}/Log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    log_file = f"{log_dir}/{seconds}_{algo_name}_log.txt"
    command += " >> {log_file} 2>&1"

    util.print_log("==============Start simulation==============")
    for dagsets_dir in os.listdir(dagsets_root_dir):
        util.print_log("Target directory: " + dagsets_dir)
        if algo_properties["preemptive"] == "true":
            util.print_log("Execution mode: NonPreemptive and Preemptive")
        else:
            util.print_log("Execution mode: NonPreemptive")

        dagsets_dir_path = os.path.join(dagsets_root_dir, dagsets_dir)
        if os.path.isdir(dagsets_dir_path):
            for i, input_dag in enumerate(os.listdir(dagsets_dir_path)):
                util.progress_bar(i, len(os.listdir(dagsets_dir_path)))
                input_dag_path = os.path.join(dagsets_dir_path, input_dag)
                if (algo_properties["input"] == "DAG" and os.path.isfile(input_dag_path)) or (
                    algo_properties["input"] == "DAGSet" and os.path.isdir(input_dag_path)
                ):
                    if os.path.isfile(input_dag_path) and not input_dag.startswith("dag_"):
                        continue

                    if algo_properties["preemptive"] == "true":
                        nonpre_output_dir = os.path.join(nonpre_output_root_dir, dagsets_dir)
                        os.makedirs(nonpre_output_dir, exist_ok=True)
                        preempt_output_dir = os.path.join(preempt_output_root_dir, dagsets_dir)
                        os.makedirs(preempt_output_dir, exist_ok=True)

                        full_command = command.format(
                            input=input_dag_path,
                            core=core_num,
                            output_dir=nonpre_output_dir,
                            preempt="",
                            log_file=log_file,
                        )
                        os.system(full_command)

                        full_command = command.format(
                            input=input_dag_path,
                            core=core_num,
                            output_dir=preempt_output_dir,
                            preempt="-p",
                            log_file=log_file,
                        )
                        os.system(full_command)

                    else:
                        output_dir = os.path.join(output_root_dir, dagsets_dir)
                        os.makedirs(output_dir, exist_ok=True)

                        full_command = command.format(
                            input=input_dag_path,
                            core=core_num,
                            output_dir=output_dir,
                            log_file=log_file,
                        )
                        os.system(full_command)

            util.progress_bar(1, 1)
            print("")


if __name__ == "__main__":
    inputs = option_parser(sys.argv[1:])

    execute_directory = inputs["execute_dir"]
    input_directory = inputs["dest_dir"]
    core_num = inputs["core"]

    execute_command_in_subdirectories(execute_directory, input_directory, core_num)
