import re
import sys
import datetime


# 各アルゴリズムに対して、入力DAGの形式、実行モード、結果の形式を定義
# "input": "DAG" or "DAGSet"
# "preemptive": "false" or "true"
# "result": "schedulability" or "boolean"
algo_list = {
    "2014_ECRTS_federated_original": {
        "input": "DAGSet",
        "preemptive": "false",
        "result": "schedulability",
    },
    "2021_RTCSA_dynfed": {"input": "DAGSet", "preemptive": "false", "result": "boolean"},
    "2013_ECRTS_basic_global_edf": {
        "input": "DAGSet",
        "preemptive": "true",
        "result": "boolean",
    },
    "2014_TPDS_basic_decomposition_based_algorithm": {
        "input": "DAGSet",
        "preemptive": "true",
        "result": "boolean",
    },
    "2020_RTSS_cpc_model_based_algorithm": {
        "input": "DAG",
        "preemptive": "false",
        "result": "boolean",
    },
}


# 文字列から数値を抽出
def extract_utilization_from_config(input_string):
    pattern = r"\d+(\.\d+)?"
    match = re.search(pattern, input_string)
    if match:
        number = float(match.group())
        return number
    else:
        print_log("Usage: For a utilization of 0.6, "
                  "the config file name must be config-06.yaml.", log_kind="ERROR")
        exit(1)


# プログレスバーを表示
def progress_bar(current, total, length=50):
    progress = current / total
    arrow = "=" * int(round(progress * length))
    spaces = " " * (length - len(arrow))
    sys.stdout.write(f"\r[{arrow + spaces}] {int(progress * 100)}%")
    sys.stdout.flush()


# ログを出力
def print_log(message, log_kind="INFO", start_time=None):
    now = datetime.datetime.now()
    if start_time is not None:
        elapsed_time = now - start_time
        message += f" ({str(elapsed_time)[:-3]})"
    print(f"{log_kind:<5s}  : {now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | {message}")
    return now


# アルゴリズムのプロパティを取得
def get_algorithm_properties(algo_name):
    if algo_name not in algo_list:
        print_log(
            "Algorithm name is not correct. Available algorithm names are:", log_kind="ERROR"
        )
        for key in algo_list.keys():
            print(f"  {key}")
        exit(1)
    return algo_list[algo_name]
