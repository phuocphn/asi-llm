from src.netlist import SPICENetlist
import glob
from calc1 import compute_cluster_metrics


data = SPICENetlist(f"data/asi-fuboco-test/small/66/")

print("netlist:", data.netlist)

# Hierarchical Level 1 Ground Truth:
# Valid subcircuit names: "MosfetDiode", "load_cap", "compesation_cap"
print("Hierarchical Level 1 Ground Truth::", data.hl1_gt)

# Hierarchical Level 2 Ground Truth:
# Valid subcircuit names:  "CM", "DiffPair", "Inverter"
print("Hierarchical Level 2 Ground Truth::", data.hl2_gt)

# Hierarchical Level 3 Ground Truth:
# Valid subcircuit names:  "firstStage", "secondStage", "thirdStage", "loadPart", "biasPart", "feedBack"
print("Hierarchical Level 3 Ground Truth::", data.hl3_gt)


hl1_prediction = [
    ("MostfetDiode", ["m11", "m12", "m8"]),
    ("load_cap", ["m21", "m22"]),
    ("compensation_cap", ["m29", "m30", "m31"]),
]

hl2_good_prediction = [
    ("DiffPair", ["m6", "m7"]),
    ("CM", ["m2", "m3", "m4"]),
    ("CM", ["m9", "m10", "m12", "m13"]),
    # ("CM", ["m3", "m7", "m4", "m2"]),
]
hl2_bad_prediction = [
    ("DiffPair", ["m6", "m7"]),
    ("CM", ["m2", "m3", "m4", "m7"]),
    ("CM", ["m1", "m10", "m12", "m13"]),
    # ("CM", ["m3", "m7", "m4", "m2"]),
]
hl3_prediction = [
    ("firstStage", ["m11", "m10"]),
]

hl1_result = compute_cluster_metrics(hl1_prediction, ground_truth=data.hl1_gt)
hl2_good_result = compute_cluster_metrics(hl2_good_prediction, ground_truth=data.hl2_gt)
hl2_bad_result = compute_cluster_metrics(hl2_bad_prediction, ground_truth=data.hl2_gt)
hl3_result = compute_cluster_metrics(hl3_prediction, ground_truth=data.hl3_gt)


print(f"{hl1_result=}")
print(f"{hl2_good_result=}")
print(f"{hl2_bad_result=}")
print(f"{hl3_result=}")
