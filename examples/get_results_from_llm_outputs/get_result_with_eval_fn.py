import json
from calc1 import average_metrics
from examples.measure_fn2 import compute_cluster_metrics_v2


def get_result(dir, key="hl3_gt"):
    stat = []
    for i in range(1, 101):
        # if "medium" in dir and i in [99, 100]:
        #     continue
        with open(dir + f"netlist_{i}/parsed_data.json", "r") as fp:
            prediction = json.load(fp)
        with open(dir + f"netlist_{i}/gt.json", "r") as fp:
            ground_truth = json.load(fp)[key]

        stat.append(compute_cluster_metrics_v2(prediction, ground_truth))

    print(average_metrics(stat))


if __name__ == "__main__":
    for subset in ["small", "medium", "large"]:
        print(f"Subset: {subset}")
        print("-" * 20)
        dir = f"outputs/instruction+following/grok-3-beta/llm_outputs/HL3/{subset}/"
        get_result(dir, key="hl3_gt")
