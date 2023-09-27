import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import glob


def option_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=False, type=str,
                        help="Directory path containing the CSV files.")
    args = parser.parse_args()

    return vars(args)


if __name__ == "__main__":
    args = option_parser(sys.argv)
    input_dir_path = args["directory"]

    # CSVファイルを全て読み込む
    csv_files = glob.glob(f"{input_dir_path}/*.csv")
    csv_files = sorted(csv_files)

    for csv_file in csv_files:
        # CSVデータの読み込み
        df = pd.read_csv(csv_file)
        # 折れ線グラフをプロット
        plt.plot(df["utilization"], df["accept"], label=f"{os.path.basename(csv_file)}",
                 marker="o", linestyle="-")
        # plt.plot(df["utilization"], df["speedup"], label=f"{os.path.basename(csv_file)}",
        #          marker="o", linestyle="-")  # (評価1)

    # グラフの詳細設定
    plt.xlabel("Max utilization")
    plt.ylabel("Acceptance of schedulable")
    # plt.ylabel("Speedup")  # (評価1)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    file_name = f"{input_dir_path}/{input_dir_path.split('/')[0]}_total.png"
    plt.savefig(file_name, bbox_inches='tight')
