import json
from calc1 import average_metrics
from examples.measure_fn2 import compute_cluster_metrics_v2 as stand_eval_fn
from calc1 import compute_cluster_metrics as strict_eval_fn
from examples.measure_fn3 import measure_fn3


def get_result(dir, key="hl3_gt"):
    stat = []
    for i in range(1, 101):
        # if "large" in dir and i in [36, 86]:
        #     continue
        # if "small" in dir and i in [34]:
        #     continue
        # if "medium" in dir and i in [99, 100]:
        #     continue

        with open(dir + f"netlist_{i}/parsed_data.json", "r") as fp:
            prediction = json.load(fp)
        with open(dir + f"netlist_{i}/gt.json", "r") as fp:
            ground_truth = json.load(fp)[key]

        stat.append(strict_eval_fn(predicted=prediction, ground_truth=ground_truth))

    print(average_metrics(stat))
    return average_metrics(stat)


if __name__ == "__main__":
    # data = {}
    # for subset in ["small", "medium", "large"]:
    #     print(f"Subset: {subset}")
    #     print("========================================")
    #     for level in ["HL1", "HL2", "HL3"]:

    #         print(f"{level=}")
    #         dir = f"outputs/table.data/instruction+following/llama3.3:70b/llm_outputs/{level}/{subset}/"
    #         # dir = f"outputs/table.data/direct+code/llama3.3:70b/llm_outputs/{level}/{subset}/"
    #         # dir = f"outputs/table.data/direct+prompting/llama3.3:70b/llm_outputs/{level}/{subset}/"

    #         get_result(dir, key=level.lower() + "_gt")
    #         # data[level] =
    data = {}
    for level in ["HL1", "HL2", "HL3"]:
        print("========================================")

        d = {}
        for subset in ["small", "medium", "large"]:

            print(f"{level=}")
            # dir = f"outputs/table.data/instruction+following/llama3.3:70b/llm_outputs/{level}/{subset}/" (ok)
            # dir = f"outputs/table.data/instruction+following/deepseek-reasoner/llm_outputs/{level}/{subset}/" (ok)
            # dir = f"outputs/table.data/instruction+following/grok-3-beta/llm_outputs/{level}/{subset}/" (ok)
            # dir = f"outputs/table.data/instruction+following-result-06.05.25/gpt-4.1/llm_outputs/{level}/{subset}/"

            # dir = f"outputs/table.data/direct+prompting/deepseek-reasoner/llm_outputs/{level}/{subset}/"
            # dir = f"results/paper-draft-09.05.2025/direct_prompting_noinstruction/llama3.3:70b/llm_outputs/{level}/{subset}/"
            # dir = f"results/paper-draft-09.05.2025/direct_prompting_noinstruction/grok-3-beta/llm_outputs/{level}/{subset}/"
            dir = f"results/paper-draft-09.05.2025/direct_prompting_noinstruction/gpt-4.1/llm_outputs/{level}/{subset}/"

            result = get_result(dir, key=level.lower() + "_gt")
            d[subset] = result

        data[level] = d
    # print(data)
    from utils import print_table_results

    print_table_results(data["HL1"], data["HL2"], data["HL3"])
