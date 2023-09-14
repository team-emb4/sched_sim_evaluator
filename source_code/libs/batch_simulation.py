import os
import sys
import argparse


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
    # 現在のディレクトリを取得
    current_dir = os.getcwd()

    # 入力DAGSet群のルートディレクトリの絶対パスを取得
    if not os.path.isabs(dagsets_root_dir):
        dagsets_root_dir = os.path.abspath(dagsets_root_dir)

    # コマンドを実行するディレクトリに移動
    os.chdir(execute_dir)

    # 現在のディレクトリ名を取得
    algorithm_dir = os.path.basename(os.getcwd())
    print("algorithm: " + algorithm_dir)

    output_root_dir = f"{current_dir}/{algorithm_dir}/SchedResult/{core_num}-cores"  # 出力先のディレクトリ

    # アルゴリズムごとに実行するコマンドを変更
    match algorithm_dir:
        case "2014_ECRTS_federated_original" | "2021_RTCSA_dynfed":
            command = "cargo run -- -d {input_dir} -c {core} -o {output_dir}"
        case "2013_ECRTS_basic_global_edf":
            command = "cargo run -- -d {input_dir} -c {core} -o {output_dir} {preempt}"
            nonpre_output_root_dir = (
                f"{current_dir}/{algorithm_dir}/SchedResult/NonPreemptive/{core_num}-cores"
            )
            preempt_output_root_dir = (
                f"{current_dir}/{algorithm_dir}/SchedResult/Preemptive/{core_num}-cores"
            )
        case "2020_RTSS_cpc_model_based_algorithm":
            # command = "cargo run -- -f {input_file} -c {core} -o {output_dir} -r {ratio}"
            command = "cargo run -- -f {input_file} -c {core} -o {output_dir}"
        case _:
            print("Algorithm name is not correct.")
            exit(1)

    for dagsets_dir in os.listdir(dagsets_root_dir):
        print("Target directory: " + dagsets_dir)
        dagsets_dir_path = os.path.join(dagsets_root_dir, dagsets_dir)
        if os.path.isdir(dagsets_dir_path):
            # 2020_RTSS_cpc_model_based_algorithmの場合はDAGファイルを引数とする
            if algorithm_dir == "2020_RTSS_cpc_model_based_algorithm":
                # サブディレクトリ内の各DAGファイルのパスをコマンドライン引数として実行する
                for dag_file in os.listdir(dagsets_dir_path):
                    dag_file_path = os.path.join(dagsets_dir_path, dag_file)
                    if os.path.isfile(dag_file_path):
                        # DAGファイルでない場合はスキップ
                        if not dag_file.startswith("dag_"):
                            continue
                        # 利用率ごとの結果出力先のサブディレクトリを作成
                        output_dir = os.path.join(output_root_dir, dagsets_dir)
                        os.makedirs(output_dir, exist_ok=True)

                        # 実行
                        full_command = command.format(
                            input_file=dag_file_path, core=core_num, output_dir=output_dir
                        )
                        print(full_command)
                        os.system(full_command)

            else:  # それ以外のアルゴリズムの場合はDAGフォルダを引数とする
                # サブディレクトリ内の各ディレクトリのパスをコマンドライン引数として実行する
                for dagset_dir in os.listdir(dagsets_dir_path):
                    dagset_dir_path = os.path.join(dagsets_dir_path, dagset_dir)
                    if os.path.isdir(dagset_dir_path):
                        # 2013_ECRTS_basic_global_edfのとき，ノンプリエンプティブとプリエンプティブで実行
                        if algorithm_dir == "2013_ECRTS_basic_global_edf":
                            # 利用率ごとの結果出力先のサブディレクトリを作成
                            # ノンプリエンプティブ用の出力先
                            nonpre_output_dir = os.path.join(nonpre_output_root_dir, dagsets_dir)
                            os.makedirs(nonpre_output_dir, exist_ok=True)
                            # プリエンプティブ用の出力先
                            preempt_output_dir = os.path.join(preempt_output_root_dir, dagsets_dir)
                            os.makedirs(preempt_output_dir, exist_ok=True)

                            # ノンプリエンプティブで実行
                            full_command = command.format(
                                input_dir=dagset_dir_path,
                                core=core_num,
                                output_dir=nonpre_output_dir,
                                preempt="",
                            )
                            print(full_command)
                            os.system(full_command)

                            # プリエンプティブで実行
                            full_command = command.format(
                                input_dir=dagset_dir_path,
                                core=core_num,
                                output_dir=preempt_output_dir,
                                preempt="-p",
                            )
                            print(full_command)
                            os.system(full_command)

                        else:  # それ以外のアルゴリズムの場合は1度だけ実行
                            # 利用率ごとの結果出力先のサブディレクトリを作成
                            output_dir = os.path.join(output_root_dir, dagsets_dir)
                            os.makedirs(output_dir, exist_ok=True)

                            full_command = command.format(
                                input_dir=dagset_dir_path, core=core_num, output_dir=output_dir
                            )
                            print(full_command)
                            os.system(full_command)


if __name__ == "__main__":
    inputs = option_parser(sys.argv[1:])

    execute_directory = inputs["execute_dir"]
    input_directory = inputs["dest_dir"]
    core_num = inputs["core"]

    # 入力されたディレクトリ内のすべてのサブディレクトリに対してコマンドを実行
    execute_command_in_subdirectories(execute_directory, input_directory, core_num)
