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

    output_root_dir = f"{current_dir}/{algorithm_dir}/SchedResult/{core_num}-cores"  # 出力先のディレクトリ
    command = "cargo run -- -d {input_dir} -c {core} -o {output_dir}"

    for dagsets_dir in os.listdir(dagsets_root_dir):
        print("Target directory: " + dagsets_dir)
        output_dir_name = dagsets_dir
        dagsets_dir_path = os.path.join(dagsets_root_dir, dagsets_dir)
        if os.path.isdir(dagsets_dir_path):
            # サブディレクトリ内の各ディレクトリのパスをコマンドライン引数として実行する
            for dagset_dir in os.listdir(dagsets_dir_path):
                dagset_dir_path = os.path.join(dagsets_dir_path, dagset_dir)
                if os.path.isdir(dagset_dir_path):
                    # 利用率ごとの結果出力先のサブディレクトリを作成
                    output_dir = os.path.join(output_root_dir, output_dir_name)
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
