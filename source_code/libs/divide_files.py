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


def divide_files_to_folders(source_folder, num_folders, output_folder_path=None):
    # 指定したフォルダにあるファイル一覧を取得
    # "dag_"で始まるファイルのみを取得
    files = [f for f in os.listdir(source_folder) if f.startswith("dag_")]

    # 対象ファイルがなければ終了
    if not files:
        print(f"No files starting with 'dag_' found in {source_folder}. Nothing to divide.")
        sys.exit(1)

    # ファイル数を取得し、ファイル数をフォルダ数で割った商と余りを計算
    num_files = len(files)
    files_per_folder, remaining_files = divmod(num_files, num_folders)

    # フォルダ名を取得
    source_folder_name = os.path.basename(os.path.dirname(source_folder))

    # フォルダ数に分ける処理
    start_index = 0
    for i in range(num_folders):
        # 新フォルダ名を"{元フォルダ名}_0", "{元フォルダ名}_1"という形式で作成
        folder_name = f"{source_folder_name}_{i}"
        folder_path = os.path.join(output_folder_path, folder_name)

        # フォルダを作成
        os.makedirs(folder_path, exist_ok=True)

        # ファイルをコピー
        num_files_in_folder = files_per_folder + (1 if i < remaining_files else 0)
        for j in range(num_files_in_folder):
            file_name = files[start_index + j]
            source_file = os.path.join(source_folder, file_name)
            output_file = os.path.join(folder_path, file_name)
            shutil.copy(source_file, output_file)

        # 次のフォルダの開始位置を更新
        start_index += num_files_in_folder


if __name__ == "__main__":
    # コマンドライン引数からフォルダのパスとフォルダ数を取得
    args = option_parser(sys.argv)

    # フォルダのパスを取得
    source_folder_path = args["source_dir"]
    output_folder_path = args["output_dir"]

    # フォルダ数を取得
    num_folders_to_create = args["num_folders"]

    # ファイルを指定したフォルダ数に分ける
    divide_files_to_folders(source_folder_path, num_folders_to_create, output_folder_path)
