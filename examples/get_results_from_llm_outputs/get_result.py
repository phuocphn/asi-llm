import json
from calc1 import average_metrics


def get_result(dir):
    stat = []
    for i in range(1, 101):
        with open(dir + f"netlist_{i}/eval_results.json", "r") as fp:
            data = json.load(fp)
        stat.append(data)

    print(average_metrics(stat))


if __name__ == "__main__":

    for subset in ["small", "medium", "large"]:
        print(f"Subset: {subset}")
        print("-" * 20)
        dir = f"outputs/table.data/instruction+following/deepseek-reasoner/llm_outputs/HL2/{subset}/"
        get_result(dir)
