import re
import sys


# 各アルゴリズムに対して、入力DAGの形式、実行モード、結果の形式を定義
# "input_DAG": "file" or "folder"
# "execution_mode": "one" or "two"
# "result": "schedulability" or "boolean"
algorithm_list = {
    "2014_ECRTS_federated_original": {
        "input_DAG": "folder",
        "execution_mode": "one",
        "result": "schedulability",
    },
    "2021_RTCSA_dynfed": {"input_DAG": "folder", "execution_mode": "one", "result": "boolean"},
    "2013_ECRTS_basic_global_edf": {
        "input_DAG": "folder",
        "execution_mode": "two",
        "result": "boolean",
    },
    "2014_TPDS_basic_decomposition_based_algorithm": {
        "input_DAG": "folder",
        "execution_mode": "two",
        "result": "boolean",
    },
    "2020_RTSS_cpc_model_based_algorithm": {
        "input_DAG": "file",
        "execution_mode": "one",
        "result": "boolean",
    },
}


# 文字列から数値を抽出
def extract_numbers_from_string(input_string):
    # 正規表現パターン: 数字の連続した部分を抽出
    pattern = r"\d+(\.\d+)?"

    # 正規表現にマッチする部分を取得
    match = re.search(pattern, input_string)

    # マッチした部分を数値に変換して返す
    if match:
        number = float(match.group())
        return number
    else:
        return None


# プログレスバーを表示
def progress_bar(current, total, length=50):
    progress = current / total
    arrow = "=" * int(round(progress * length))
    spaces = " " * (length - len(arrow))
    sys.stdout.write(f"\r[{arrow + spaces}] {int(progress * 100)}%")
    sys.stdout.flush()
