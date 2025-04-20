from src.netlist import SPICENetlist
from generate_scripts.grok_medium_56.cm import extract_current_mirrors
from generate_scripts.grok_medium_56.dp import identify_differential_pairs
from generate_scripts.grok_medium_56.inv import identify_inverters
import glob
import json
from calc1 import compute_cluster_metrics, average_metrics


def test_single_example():
    # data = SPICENetlist(f"data/benchmark-asi-100/small/1/")
    data = SPICENetlist(f"data/asi-fuboco-train/medium/56/")

    cm = extract_current_mirrors(data.netlist)
    # print(cm)
    dp = identify_differential_pairs(data.netlist)
    # print(dp)
    invs = identify_inverters(data.netlist)
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
            cm = extract_current_mirrors(data.netlist)
            dp = identify_differential_pairs(data.netlist)
            invs = identify_inverters(data.netlist)
            hl2_prediction = cm + dp + invs
            # print(hl2_prediction)
            results.append(
                compute_cluster_metrics(
                    predicted=hl2_prediction, ground_truth=data.hl2_gt
                )
            )
        info[subset] = average_metrics(results)
    return info


# test_single_example()
print(json.dumps(test_category(), indent=2))
