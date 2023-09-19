import sys
import os
import yaml
import matplotlib.pyplot as plt

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
def count_results(root_log_dir_path):
    if not os.path.isabs(root_log_dir_path):
        root_log_dir_path = os.path.abspath(root_log_dir_path)

    algo_dir = root_log_dir_path.split("/SchedResult")[0]
    algo_name = os.path.basename(algo_dir)
    algo_properties = get_algorithm_properties(algo_name)  # アルゴリズムのプロパティを取得
    if algo_properties["preemptive"] == "true":
        pre = os.path.basename(os.path.dirname(root_log_dir_path))
        util.print_log("Target algorithm: " + algo_name + "-" + pre)
    else:
        util.print_log("Target algorithm: " + algo_name)

    log_dir_count = len(os.listdir(root_log_dir_path))
    max_utilization = [0] * log_dir_count
    yaml_count = [0] * log_dir_count
    schedulable_count = [0] * log_dir_count
    unschedulable_count = [0] * log_dir_count
    true_count = [0] * log_dir_count
    false_count = [0] * log_dir_count

    dir_list = os.listdir(root_log_dir_path)
    dir_list.sort()
    for i, log_dir in enumerate(dir_list):
        util.print_log("Target directory: " + log_dir)
        utilization = util.extract_numbers_from_string(log_dir)
        if utilization is None:
            continue
        max_utilization[i] = utilization

        log_dir = os.path.join(root_log_dir_path, log_dir)
        log_file_list = os.listdir(log_dir)
        for j, file_name in enumerate(log_file_list):
            util.progress_bar(j, len(log_file_list))
            if file_name.endswith(".yaml"):
                yaml_count[i] += 1
                log_file_path = os.path.join(log_dir, file_name)
                log_data = read_yaml_file(log_file_path)

                if algo_properties["result"] == "schedulability":
                    if isinstance(log_data["result"], SchedulableTag):
                        schedulable_count[i] += 1
                    elif isinstance(log_data["result"], UnschedulableTag):
                        unschedulable_count[i] += 1
                    else:
                        print("Unknown Result")

                else:  # resultがtrueまたはfalseで表される場合
                    if log_data["result"]:
                        true_count[i] += 1
                    else:
                        false_count[i] += 1

        util.progress_bar(1, 1)
        print("")

    print("==============Result==============")
    accept = [0.0] * log_dir_count
    for i, subdir in enumerate(dir_list):
        print(f"Directory: {subdir}")
        print(f"  Max utilization: {max_utilization[i]}")
        print(f"  Number of .yaml files: {yaml_count[i]}")
        if algo_properties["result"] == "schedulability":
            print(f"  Number of schedulable: {schedulable_count[i]}")
            print(f"  Number of schedulable: {unschedulable_count[i]}")
            accept[i] = schedulable_count[i] / yaml_count[i]
            print(f"  Acceptance of schedulable: {accept[i]}")
        else:
            print(f"  Number of true: {true_count[i]}")
            print(f"  Number of false: {false_count[i]}")
            accept[i] = true_count[i] / yaml_count[i]
            print(f"  Acceptance of true: {accept[i]}")
        print("")

    print("Total:")
    print(f"  Number of directories: {sum(yaml_count)}")
    if algo_properties["result"] == "schedulability":
        print(f"  Number of schedulable: {sum(schedulable_count)}")
        print(f"  Number of unschedulable: {sum(unschedulable_count)}")
        print(f"  Acceptance of schedulable: {sum(schedulable_count) / sum(yaml_count)}")
    else:
        print(f"  Number of true: {sum(true_count)}")
        print(f"  Number of false: {sum(false_count)}")
        print(f"  Acceptance of true: {sum(true_count) / sum(yaml_count)}")
    print("")
    print("==================================")

    core = os.path.basename(root_log_dir_path)
    plt.figure()
    # 縦軸: Acceptance of schedulable(true)
    # 横軸: Max utilization
    plt.plot(max_utilization, accept, marker="o", color="blue", linestyle="-")
    plt.xlabel("Max utilization")
    if algo_properties["result"] == "schedulability":
        plt.ylabel("Acceptance of schedulable")
    else:
        plt.ylabel("Acceptance of true")

    os.makedirs(f"{algo_dir}/OutputsResult", exist_ok=True)
    if algo_properties["preemptive"] == "true":
        plt.savefig(
            f"{algo_dir}/OutputsResult/plot_accept_{algo_name}_{pre}_{core}-cores.png"
        )
    else:
        plt.savefig(f"{algo_dir}/OutputsResult/plot_accept_{algo_name}_{core}-cores.png")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python result_check.py /path/to/your/directory")
        sys.exit(1)

    input_directory = sys.argv[1]
    count_results(input_directory)
