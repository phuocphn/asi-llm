from src.netlist import SPICENetlist
from generate_scripts.gpt4o_medium_56.cm import parse_netlist as cm_parse_netlist
from generate_scripts.gpt4o_medium_56.cm import find_current_mirrors
from generate_scripts.gpt4o_medium_56.inv_fixed import extract_inverters_from_netlist
from generate_scripts.gpt4o_medium_56.dp import parse_netlist as dp_parse_netlist
from generate_scripts.gpt4o_medium_56.dp import find_diff_pairs
import glob
import json
from calc1 import compute_cluster_metrics, average_metrics


def test_single_example():
    # data = SPICENetlist(f"data/benchmark-asi-100/small/1/")
    data = SPICENetlist(f"data/asi-fuboco-train/medium/56/")

    cm = find_current_mirrors(cm_parse_netlist(data.netlist))
    # print(cm)
    dp = find_diff_pairs(dp_parse_netlist(data.netlist))
    # print(dp)
    invs = extract_inverters_from_netlist(data.netlist)
    # print(invs)

    hl2_prediction = cm + dp + invs
    print(hl2_prediction)

    print(compute_cluster_metrics(predicted=hl2_prediction, ground_truth=data.hl2_gt))


def test_category(subsets=["small", "medium", "large"]):
    info = {}
    for subset in subsets:
        results = []
        for i in range(1, 101):
            data = SPICENetlist(f"data/asi-fuboco-test/{subset}/{i}/")
            cm = find_current_mirrors(cm_parse_netlist(data.netlist))
            dp = find_diff_pairs(dp_parse_netlist(data.netlist))
            invs = extract_inverters_from_netlist(data.netlist)
            hl2_prediction = cm + dp + invs
            # print(hl2_prediction)
            results.append(
                compute_cluster_metrics(
                    predicted=hl2_prediction, ground_truth=data.hl2_gt
                )
            )
        info[subset] = average_metrics(results)
    return info


print(json.dumps(test_category(), indent=2))
