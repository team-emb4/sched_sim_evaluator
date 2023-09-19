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
        "-n", "--num_folders", required=True, type=int, help="number of folders to divide into."
    )
    parser.add_argument("-o", "--output_dir", type=str, help="path to output directory.")
    args = parser.parse_args()

    return vars(args)


# ファイル群を指定したフォルダ数に分ける
def divide_files_to_folders(source_folder, num_folders, output_folder_path=None):
    files = [f for f in os.listdir(source_folder) if f.startswith("dag_")]
    if not files:
        print(f"No files starting with 'dag_' found in {source_folder}. Nothing to divide.")
        sys.exit(1)

    num_files = len(files)
    files_per_folder, remaining_files = divmod(num_files, num_folders)
    source_folder_name = os.path.basename(os.path.dirname(source_folder))
    source_file_index = 0
    for i in range(num_folders):
        new_folder_name = f"{source_folder_name}_{i}"
        new_folder_path = os.path.join(output_folder_path, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        num_files_in_folder = files_per_folder + (1 if i < remaining_files else 0)
        for j in range(num_files_in_folder):
            file_name = files[source_file_index + j]
            source_file = os.path.join(source_folder, file_name)
            output_file = os.path.join(new_folder_path, file_name)
            shutil.copy(source_file, output_file)

        # 次のフォルダにコピーするファイルの開始位置を更新
        source_file_index += num_files_in_folder


if __name__ == "__main__":
    args = option_parser(sys.argv)

    source_folder_path = args["source_dir"]
    output_folder_path = args["output_dir"]
    num_folders_to_create = args["num_folders"]

    divide_files_to_folders(source_folder_path, num_folders_to_create, output_folder_path)
