from src.netlist import SPICENetlist
import glob
from calc1 import compute_cluster_metrics


data = SPICENetlist(f"data/asi-fuboco-test/small/1/")

print("netlist:", data.netlist)

# ground truth of hierarchial level 1 (HL1):  devices (diode-connected transistors, load/comprensation caps)
print("hl1_gt:", data.hl1_gt)

# ground truth of hierarchial level 21 (HL2):   structure pair (diffpair, cm, inverter)
print("hl2_gt:", data.hl2_gt)
print("hl3_gt:", data.hl3_gt)


hl1prediction = [
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
print(compute_cluster_metrics(hl1prediction, ground_truth=data.hl1_gt))
print(compute_cluster_metrics(hl2_prediction, ground_truth=data.hl2_gt))
print(compute_cluster_metrics(hl3_prediction, ground_truth=data.hl3_gt))
