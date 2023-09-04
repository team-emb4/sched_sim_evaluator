import re


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
