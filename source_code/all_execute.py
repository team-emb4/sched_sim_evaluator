import os
import sys
import argparse


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--execute_dir", required=True, type=str, help="path to execute directory."
    )
    parser.add_argument(
        "-d", "--dest_dir", required=True, type=str, help="path to destination directory."
    )
    parser.add_argument("-c", "--core", required=True, type=int, help="number of cores")
    args = parser.parse_args()

    return vars(args)


def execute_command_in_subdirectories(execute_dir, root_dir, core_num):
    # このファイルのパスを取得
    script_path = os.path.abspath(__file__)

    # このファイルがあるディレクトリを取得
    script_dir = os.path.dirname(script_path)

    # 入力ディレクトリの絶対パスを取得
    if not os.path.isabs(root_dir):
        root_dir = os.path.abspath(root_dir)

    # コマンドを実行するディレクトリに移動
    os.chdir(execute_dir)

    # 現在のディレクトリ名を取得
    algorithm_dir = os.path.basename(os.getcwd())

    output_root_dir = f"{script_dir}/{algorithm_dir}/SchedResult/{core_num}-cores"  # 出力先のディレクトリ
    command = "cargo run -- -d {input_dir} -c {core} -o {output_dir}"

    for subdir in os.listdir(root_dir):
        print("Target directory: " + subdir)
        output_dir_name = subdir
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            # サブディレクトリ内の各ディレクトリのパスをコマンドライン引数として実行する
            for dir_in_subdir in os.listdir(subdir_path):
                dir_path = os.path.join(subdir_path, dir_in_subdir)
                if os.path.isdir(dir_path):
                    output_subdir = os.path.join(output_root_dir, output_dir_name)
                    # 出力先のサブディレクトリを作成
                    os.makedirs(output_subdir, exist_ok=True)

                    full_command = command.format(
                        input_dir=dir_path, core=core_num, output_dir=output_subdir
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
