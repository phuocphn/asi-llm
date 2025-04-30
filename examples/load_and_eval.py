from src.netlist import SPICENetlist
import glob
from calc1 import compute_cluster_metrics


data = SPICENetlist(f"data/asi-fuboco-test/small/1/")

print("netlist:", data.netlist)

# Hierarchical Level 1 Ground Truth:
# Valid keys: "MosfetDiode", "load_cap", "compesation_cap"
print("hl1_gt:", data.hl1_gt)

# Hierarchical Level 2 Ground Truth:
# Valid keys: "CM", "DiffPair", "Inverter"
print("hl2_gt:", data.hl2_gt)

# Hierarchical Level 3 Ground Truth:
# Valid keys: "firstStage", "secondStage", "thirdStage", "loadPart", "biasPart", "feedBack"
print("hl3_gt:", data.hl3_gt)


hl1_prediction = [
    {"sub_circuit_name": "MostfetDiode", "transistor_names": ["m11", "m12", "m8"]},
    {"sub_circuit_name": "load_cap", "transistor_names": ["m21", "m22"]},
    {"sub_circuit_name": "compensation_cap", "transistor_names": ["m29", "m30", "m31"]},
]

hl2_prediction = [
    {"sub_circuit_name": "DiffPair", "transistor_names": ["m11", "m12"]},
    {"sub_circuit_name": "DiffPair", "transistor_names": ["m6", "m8"]},
    {"sub_circuit_name": "CM", "transistor_names": ["m2", "m3", "m4", "m5"]},
    {"sub_circuit_name": "CM", "transistor_names": ["m10", "m11", "m12"]},
    {"sub_circuit_name": "CM", "transistor_names": ["m21", "m22"]},
    {"sub_circuit_name": "CM", "transistor_names": ["m29", "m30", "m31"]},
]
hl3_prediction = [
    {"sub_circuit_name": "firstStage", "transistor_names": ["m11", "m10"]},
]

hl1_result = compute_cluster_metrics(hl1_prediction, ground_truth=data.hl1_gt)
hl2_result = compute_cluster_metrics(hl2_prediction, ground_truth=data.hl2_gt)
hl3_result = compute_cluster_metrics(hl3_prediction, ground_truth=data.hl3_gt)

assert {
    "Precision": 0.25,
    "Recall": 0.3333333333333333,
    "F1-score": 0.28571428571428575,
} == hl1_result

assert {"Precision": 0.0, "Recall": 0.0, "F1-score": 0} == hl2_result
assert {"Precision": 1.0, "Recall": 0.14285714285714285, "F1-score": 0.25} == hl3_result
print(hl1_result)
print(hl2_result)
print(hl3_result)
