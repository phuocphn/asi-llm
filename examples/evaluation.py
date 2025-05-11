from src.netlist import SPICENetlist
import glob
import re
import json
from calc1 import compute_cluster_metrics, average_metrics
from typing import List, Tuple, Dict, Set, Any
from collections import defaultdict, deque, Counter
import itertools


def code_eval(subsets=["small", "medium", "large"]):
    hl1_info = {}
    hl2_info = {}
    hl3_info = {}

    for subset in subsets:
        hl1_results = []
        hl2_results = []
        hl3_results = []

        for i in range(1, 101):
            data = SPICENetlist(f"data/asi-fuboco-test/{subset}/{i}/")

            hl1_results.append(
                compute_cluster_metrics(
                    predicted=findSubCircuitHL1(data.netlist), ground_truth=data.hl1_gt
                )
            )

            cm = findSubCircuitCM(data.netlist)
            dp = findSubCircuitDiffPair(data.netlist)
            invs = findSubCircuitInverter(data.netlist)
            hl2_prediction = cm + dp + invs
            hl2_results.append(
                compute_cluster_metrics(
                    predicted=hl2_prediction, ground_truth=data.hl2_gt
                )
            )

            hl3_results.append(
                compute_cluster_metrics(
                    predicted=findSubCircuitHL3(data.netlist), ground_truth=data.hl3_gt
                )
            )

        hl1_info[subset] = average_metrics(hl1_results)
        hl2_info[subset] = average_metrics(hl2_results)
        hl3_info[subset] = average_metrics(hl3_results)

    return hl1_info, hl2_info, hl3_info


hl1_info, hl2_info, hl3_info = code_eval()
print("HL1 Evaluation")
print("==" * 20)
print(json.dumps(hl1_info, indent=2))

print("HL2 Evaluation")
print("==" * 20)
print(json.dumps(hl2_info, indent=2))

print("HL3 Evaluation")
print("==" * 20)
print(json.dumps(hl3_info, indent=2))
