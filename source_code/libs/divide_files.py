import os
import shutil
import sys
import argparse


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--source_dir", required=True, type=str, help="path to source directory."
    )
    parser.add_argument(
        "-n", "--num_dirs", required=True, type=int, help="number of dirs to divide into."
    )
    parser.add_argument("-o", "--output_dir", type=str, help="path to output directory.")
    args = parser.parse_args()

    return vars(args)


# ファイル群を指定したフォルダ数に分ける
def divide_dag_files_to_dirs(input_dir_path, num_dirs, output_dir_path=None):
    dag_file_list = [f for f in os.listdir(input_dir_path) if f.startswith("dag_")]
    if not dag_file_list:
        print(f"No files starting with 'dag_' found in {input_dir_path}. Nothing to divide.")
        sys.exit(1)

    files_per_dir, remaining_files = divmod(len(dag_file_list), num_dirs)
    input_file_index = 0
    for i in range(num_dirs):
        output_dagset_dir_path = os.path.join(output_dir_path, f"DAGs_{i}")
        os.makedirs(output_dagset_dir_path, exist_ok=True)

        num_files_in_dir = files_per_dir + (1 if i < remaining_files else 0)
        for _ in range(num_files_in_dir):
            dag_file_name = dag_file_list[input_file_index]
            shutil.copy(os.path.join(input_dir_path, dag_file_name),
                        os.path.join(output_dagset_dir_path, dag_file_name))
            input_file_index += 1


if __name__ == "__main__":
    args = option_parser(sys.argv)

    input_dir_path = args["source_dir"]
    output_dir_path = args["output_dir"]
    num_dirs_to_create = args["num_dirs"]

    divide_dag_files_to_dirs(input_dir_path, num_dirs_to_create, output_dir_path)
