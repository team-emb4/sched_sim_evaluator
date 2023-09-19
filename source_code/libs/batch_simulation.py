import os
import sys
import argparse
import datetime

from libs import util
from libs.util import algo_list


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


def execute_command_in_subdirectories(execute_dir, dagsets_root_dir, core_num):
    now = datetime.datetime.now()
    seconds = now.strftime("%Y-%m-%d-%H-%M-%S")
    current_dir = os.getcwd()

    # 入力DAGSet群のルートディレクトリの絶対パスを取得
    if not os.path.isabs(dagsets_root_dir):
        dagsets_root_dir = os.path.abspath(dagsets_root_dir)

    # コマンドを実行するディレクトリに移動
    os.chdir(execute_dir)

    # 現在のディレクトリ名を取得
    algorithm = os.path.basename(os.getcwd())
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
        util.print_log("Target algorithm: " + algorithm)

    # スケジュール結果の出力先のディレクトリパス
    output_root_dir = f"{current_dir}/{algorithm}/SchedResult/{core_num}-cores"

    # アルゴリズムごとに実行するコマンドを変更
    match properties:
        case {"input_DAG": "folder", "execution_mode": "one"}:
            command = "cargo run -- -d {input_DAG} -c {core} -o {output_dir}"
        case {"input_DAG": "folder", "execution_mode": "two"}:
            command = "cargo run -- -d {input_DAG} -c {core} -o {output_dir} {preempt}"
            nonpre_output_root_dir = (
                f"{current_dir}/{algorithm}/SchedResult/NonPreemptive/{core_num}-cores"
            )
            preempt_output_root_dir = (
                f"{current_dir}/{algorithm}/SchedResult/Preemptive/{core_num}-cores"
            )
        case {"input_DAG": "file", "execution_mode": "one"}:
            # command = "cargo run -- -f {input_file} -c {core} -o {output_dir} -r {ratio}"
            command = "cargo run -- -f {input_DAG} -c {core} -o {output_dir}"
        case _:  # それ以外の場合はエラー
            # アルゴリズムのプロパティが正しく設定されていない場合はエラー
            util.print_log("Algorithm properties are not correct.", log_kind="ERROR")
            exit(1)

    util.print_log(f"Core number: {core_num}")

    # SchedResultに指定したコア数のディレクトリがすでに存在する場合は、実行を続けるかどうかを確認
    # 実行を続ける場合は、すでに存在するディレクトリを削除
    if (properties["execution_mode"] == "two" and os.path.exists(nonpre_output_root_dir)) or (
        properties["execution_mode"] == "one" and os.path.exists(output_root_dir)
    ):
        util.print_log(f"Simulation results for {core_num}-core are already exists.")
        util.print_log("Do you want to continue and delete the existing results? (y/n)")
        answer = input()
        if answer == "y" or answer == "Y":
            util.print_log("Deleted the existing results")
            if properties["execution_mode"] == "two":
                os.system(f"rm -rf {nonpre_output_root_dir}")
                os.system(f"rm -rf {preempt_output_root_dir}")
            else:
                os.system(f"rm -rf {output_root_dir}")
        else:
            util.print_log("Exit.")
            exit(1)

    # log出力ディレクトリを作成
    log_dir = f"{current_dir}/{algorithm}/Log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    # logファイル名は"年月日時分秒_アルゴリズム名_log.txt"
    log_file = f"{log_dir}/{seconds}_{algorithm}_log.txt"

    # コマンドの最後にリダイレクトを追加
    command += " >> {log_file} 2>&1"

    util.print_log("==============Start simulation==============")

    for dagsets_dir in os.listdir(dagsets_root_dir):
        util.print_log("Target directory: " + dagsets_dir)
        # 実行モードを表示
        if properties["execution_mode"] == "two":
            util.print_log("Execution mode: NonPreemptive and Preemptive")
        else:
            util.print_log("Execution mode: NonPreemptive")

        dagsets_dir_path = os.path.join(dagsets_root_dir, dagsets_dir)
        if os.path.isdir(dagsets_dir_path):
            # サブディレクトリ内の各DAGファイルのパスをコマンドライン引数として実行する
            for i, input_dag in enumerate(os.listdir(dagsets_dir_path)):
                # プログレスバーを表示
                util.progress_bar(i, len(os.listdir(dagsets_dir_path)))

                input_dag_path = os.path.join(dagsets_dir_path, input_dag)  # 入力DAGのパス

                # プロパティと入力DAGの形式が一致している場合のみ実行
                if (properties["input_DAG"] == "file" and os.path.isfile(input_dag_path)) or (
                    properties["input_DAG"] == "folder" and os.path.isdir(input_dag_path)
                ):
                    # DAGファイルでない場合はスキップ
                    if os.path.isfile(input_dag_path) and not input_dag.startswith("dag_"):
                        continue

                    # 実行モードが2種類ある場合はノンプリエンプティブとプリエンプティブで実行
                    if properties["execution_mode"] == "two":
                        # 利用率ごとの結果出力先のサブディレクトリを作成
                        # ノンプリエンプティブ用の出力先
                        nonpre_output_dir = os.path.join(nonpre_output_root_dir, dagsets_dir)
                        os.makedirs(nonpre_output_dir, exist_ok=True)
                        # プリエンプティブ用の出力先
                        preempt_output_dir = os.path.join(preempt_output_root_dir, dagsets_dir)
                        os.makedirs(preempt_output_dir, exist_ok=True)

                        # ノンプリエンプティブで実行
                        full_command = command.format(
                            input_DAG=input_dag_path,
                            core=core_num,
                            output_dir=nonpre_output_dir,
                            preempt="",
                            log_file=log_file,
                        )
                        os.system(full_command)

                        # プリエンプティブで実行
                        full_command = command.format(
                            input_DAG=input_dag_path,
                            core=core_num,
                            output_dir=preempt_output_dir,
                            preempt="-p",
                            log_file=log_file,
                        )
                        os.system(full_command)

                    else:  # それ以外のアルゴリズムの場合は1度だけ実行
                        # 利用率ごとの結果出力先のサブディレクトリを作成
                        output_dir = os.path.join(output_root_dir, dagsets_dir)
                        os.makedirs(output_dir, exist_ok=True)

                        # 実行
                        full_command = command.format(
                            input_DAG=input_dag_path,
                            core=core_num,
                            output_dir=output_dir,
                            log_file=log_file,
                        )
                        os.system(full_command)

            # プログレスバーを表示
            util.progress_bar(1, 1)
            print("")


if __name__ == "__main__":
    inputs = option_parser(sys.argv[1:])

    execute_directory = inputs["execute_dir"]
    input_directory = inputs["dest_dir"]
    core_num = inputs["core"]

    # 入力されたディレクトリ内のすべてのサブディレクトリに対してコマンドを実行
    execute_command_in_subdirectories(execute_directory, input_directory, core_num)
