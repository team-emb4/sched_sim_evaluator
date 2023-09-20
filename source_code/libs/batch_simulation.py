import os
import sys
import argparse

from libs import util
from libs.util import get_algorithm_properties


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--execute_dir", required=True, type=str, help="path to execute directory."
    )
    parser.add_argument(
        "-d",
        "--input_tasks_dir",
        required=True,
        type=str,
        help="path to input tasks directory.",
    )
    parser.add_argument("-c", "--core", required=True, type=int, help="number of cores")
    args = parser.parse_args()

    return vars(args)


# 全てのinput(DAGSet or DAG)に対してシミュレーションを実行する
def run_simulation_for_all_inputs(simulator_dir, root_input_tasks_dir, core_num):
    cwd = os.getcwd()
    if not os.path.isabs(root_input_tasks_dir):
        root_input_tasks_dir = os.path.abspath(root_input_tasks_dir)

    os.chdir(simulator_dir)
    algo_name = os.path.basename(os.getcwd())
    util.print_log("Target algorithm: " + algo_name)
    util.print_log(f"Core number: {core_num}")

    # 実行コマンドの作成
    algo_properties = get_algorithm_properties(algo_name)
    match algo_properties:
        case {"input": "DAGSet", "preemptive": "false"}:
            command = "cargo run -- -d {input} -c {core} -o {output_dir}"
        case {"input": "DAGSet", "preemptive": "true"}:
            command = "cargo run -- -d {input} -c {core} -o {output_dir} {preempt}"
        case {"input": "DAG", "preemptive": "false"}:
            command = "cargo run -- -f {input} -c {core} -o {output_dir}"
        case _: exit(1)
    # command += " > /dev/null 2>&1"

    # 出力ルートディレクトリの作成
    output_root_dir = f"{cwd}/{algo_name}/SchedResult/{core_num}-cores"
    nonpre_output_root_dir = f"{cwd}/{algo_name}/SchedResult/NonPreemptive/{core_num}-cores"
    preempt_output_root_dir = f"{cwd}/{algo_name}/SchedResult/Preemptive/{core_num}-cores"

    # 出力ルートディレクトリの存在確認　存在する場合は削除or終了
    if (algo_properties["preemptive"] == "true" and os.path.exists(nonpre_output_root_dir)) or (
        algo_properties["preemptive"] == "false" and os.path.exists(output_root_dir)
    ):
        util.print_log(f"Simulation results for {core_num}-core are already exists.")
        util.print_log("Do you want to continue and delete the existing results? (y/n)")
        answer = input().lower()
        if answer == "y":
            util.print_log("Deleted the existing results")
            if algo_properties["preemptive"] == "true":
                os.system(f"rm -rf {nonpre_output_root_dir}")
                os.system(f"rm -rf {preempt_output_root_dir}")
            else:
                os.system(f"rm -rf {output_root_dir}")
        else:
            util.print_log("Exit.")
            exit(1)

    # 入力ルートディレクトリ下の各ディレクトリに対して実行
    util.print_log("==============Start simulation==============")
    for input_tasks_dir in sorted(os.listdir(root_input_tasks_dir)):
        util.print_log("Input directory: " + input_tasks_dir)
        if algo_properties["preemptive"] == "true":
            util.print_log("Execution mode: NonPreemptive and Preemptive")
        else:
            util.print_log("Execution mode: NonPreemptive")

        input_tasks_dir_path = os.path.join(root_input_tasks_dir, input_tasks_dir)
        input_tasks_dir_list = os.listdir(input_tasks_dir_path)
        # 各ディレクトリ下の各ディレクトリやファイルに対して実行
        for i, input_task in enumerate(input_tasks_dir_list):
            util.progress_bar(i, len(input_tasks_dir_list))
            input_task_path = os.path.join(input_tasks_dir_path, input_task)
            # configファイルはスキップ
            if os.path.isfile(input_task_path) and not input_task.startswith("dag_"):
                continue
            print("check")
            if algo_properties["preemptive"] == "true":
                create_and_execute_command(command, nonpre_output_root_dir,
                                           input_tasks_dir, input_task_path, core_num)
                create_and_execute_command(command, preempt_output_root_dir,
                                           input_tasks_dir, input_task_path, core_num, "-p")
            else:
                create_and_execute_command(command, output_root_dir, input_tasks_dir,
                                           input_task_path, core_num)

        util.progress_bar(1, 1)
        print("")


def create_and_execute_command(command, root_dir, task_dir, input_path, core, preempt_option=""):
    output_dir = os.path.join(root_dir, task_dir)
    os.makedirs(output_dir, exist_ok=True)
    full_command = command.format(
        input=input_path,
        core=core,
        output_dir=output_dir,
        preempt=preempt_option
    )
    os.system(full_command)


if __name__ == "__main__":
    inputs = option_parser(sys.argv[1:])

    execute_directory = inputs["execute_dir"]
    input_directory = inputs["input_tasks_dir"]
    core_num = inputs["core"]

    run_simulation_for_all_inputs(execute_directory, input_directory, core_num)
