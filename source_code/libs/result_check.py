import sys
import os
import yaml
import matplotlib.pyplot as plt
import csv

from libs import util
from libs.util import get_algorithm_properties


# !Schedulableタグの定義
class SchedulableTag:
    def __init__(self, high_dedicated_cores, low_dedicated_cores):
        self.high_dedicated_cores = high_dedicated_cores
        self.low_dedicated_cores = low_dedicated_cores


# !Unschedulableタグの定義
class UnschedulableTag:
    def __init__(self, reason, insufficient_cores):
        self.reason = reason
        self.insufficient_cores = insufficient_cores


# JobEventTimesタグの定義
class JobEventTimes:
    def __init__(self, time):
        self.time = time


# カスタムタグのコンストラクタ
def custom_constructor_schedulable(loader, node):
    data = loader.construct_mapping(node, deep=True)
    return SchedulableTag(**data)


def custom_constructor_unschedulable(loader, node):
    data = loader.construct_mapping(node, deep=True)
    return UnschedulableTag(**data)


def custom_constructor_job_event(loader, node):
    data = loader.construct_scalar(node)
    return JobEventTimes(int(data))


# カスタムタグを登録
yaml.SafeLoader.add_constructor("!Schedulable", custom_constructor_schedulable)
yaml.SafeLoader.add_constructor("!Unschedulable", custom_constructor_unschedulable)
yaml.SafeLoader.add_constructor("!StartTime", custom_constructor_job_event)
yaml.SafeLoader.add_constructor("!ResumeTime", custom_constructor_job_event)
yaml.SafeLoader.add_constructor("!FinishTime", custom_constructor_job_event)
yaml.SafeLoader.add_constructor("!PreemptedTime", custom_constructor_job_event)


# yamlファイルを読み込み
def read_yaml_file(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return data


# ディレクトリ内のyamlファイル群から、スケジュール成功とスケジュール失敗の数をカウント
def count_results(root_result_dir_path):
    if not os.path.isabs(root_result_dir_path):
        root_result_dir_path = os.path.abspath(root_result_dir_path)

    algo_dir_path = root_result_dir_path.split("/SchedResult")[0]
    algo_name = os.path.basename(algo_dir_path)
    algo_properties = get_algorithm_properties(algo_name)
    preempt_type = os.path.basename(os.path.dirname(root_result_dir_path))

    log_message = "Target algorithm: " + algo_name
    if algo_properties.get("preemptive") == "true":
        log_message += f" [{preempt_type}]"
    util.print_log(log_message)

    result_dir_list = sorted(os.listdir(root_result_dir_path))
    result_dir_count = len(result_dir_list)
    result_stats = {
        "max_utilization": [0] * result_dir_count,
        "yaml_count": [0] * result_dir_count,
        "true_count": [0] * result_dir_count,
        "false_count": [0] * result_dir_count,
        "accept": [0.0] * result_dir_count,
    }

    for i, result_dir in enumerate(result_dir_list):
        util.print_log("Target directory: " + result_dir)

        result_stats["max_utilization"][i] = util.extract_utilization_from_name(result_dir)

        result_dir_path = os.path.join(root_result_dir_path, result_dir)
        result_file_list = os.listdir(result_dir_path)
        for j, result_file_name in enumerate(result_file_list):
            util.progress_bar(j, len(result_file_list))
            result_stats["yaml_count"][i] += 1
            result = read_yaml_file(os.path.join(result_dir_path, result_file_name))["result"]
            if isinstance(result, UnschedulableTag) or not result:
                result_stats["false_count"][i] += 1
            else:
                result_stats["true_count"][i] += 1

        util.progress_bar(1, 1)
        print("")

    for i in range(len(result_dir_list)):
        result_stats["accept"][i] = result_stats["true_count"][i] / result_stats["yaml_count"][i]

    os.makedirs(f"{algo_dir_path}/OutputsResult", exist_ok=True)
    plt.figure()
    plt.plot(result_stats["max_utilization"], result_stats["accept"],
             marker="o", color="blue", linestyle="-")
    plt.xlabel("Max utilization")
    plt.ylabel("Acceptance of schedulable")
    core_num = os.path.basename(root_result_dir_path)
    if algo_properties["preemptive"] == "true":
        file_name = f"{algo_dir_path}/OutputsResult/{algo_name}_{preempt_type}_{core_num}.png"
    else:
        file_name = f"{algo_dir_path}/OutputsResult/{algo_name}_{core_num}.png"
    plt.savefig(file_name)

    data = [["utilization", "accept"]]
    for i in range(len(result_dir_list)):
        data.append([result_stats["max_utilization"][i], result_stats["accept"][i]])

    with open(f"{algo_dir_path}/OutputsResult/{algo_name}_{preempt_type}_{core_num}.csv",
              "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python result_check.py /path/to/your/directory")
        sys.exit(1)

    input_directory = sys.argv[1]
    count_results(input_directory)
