import glob
import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd
from src.netlist import SPICENetlist


def get_rawlabels_statistic(data_path="data/asi-fuboco-test"):
    instance_counts = defaultdict(int)
    circuit_counts = defaultdict(set)
    for dir in ["small", "medium", "large"]:

        for i in range(1, 101):
            netlist_dir = f"{data_path}/{dir}/{i}/"

            tree = ET.parse(
                glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0]
            )
            root = tree.getroot()
            subcircuits = root[1]

            for sc in subcircuits:
                circuit_name = sc.attrib["name"]
                circuit_name = circuit_name[: circuit_name.find("[")]
                circuit_counts[circuit_name].add(netlist_dir)
                instance_counts[circuit_name] += 1

    return instance_counts, circuit_counts


def get_labels_statistic(data_path="data/asi-fuboco-test"):
    instance_counts = defaultdict(int)
    circuit_counts = defaultdict(set)
    for dir in ["small", "medium", "large"]:

        for i in range(1, 101):
            netlist_dir = f"{data_path}/{dir}/{i}/"
            data = SPICENetlist(netlist_dir)

            # for sc in data.hl2_gt:
            #     subcircuit_name = sc["sub_circuit_name"]
            #     circuit_counts[subcircuit_name].add(netlist_dir)
            #     instance_counts[subcircuit_name] += 1

            tree = ET.parse(
                glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0]
            )
            root = tree.getroot()
            subcircuits = root[1]
            for dtype, components in data.hl1_gt:
                # pass
                circuit_counts[dtype].add(netlist_dir)
                instance_counts[dtype] += len(components)

            for sc in subcircuits:
                circuit_name = sc.attrib["name"]
                circuit_name = circuit_name[: circuit_name.find("[")]
                if circuit_name in [
                    "MosfetDiodeArray",
                    "CapacitorArray",
                    "MosfetNormalArray",
                ]:
                    continue
                circuit_counts[circuit_name].add(netlist_dir)
                instance_counts[circuit_name] += 1

            for par_type, components in data.hl3_gt:
                par_type = par_type
                circuit_counts[par_type].add(netlist_dir)
                instance_counts[par_type] += 1

    return instance_counts, circuit_counts


if __name__ == "__main__":
    """Get list of netlist contains particular subcircuit name"""

    instance_counts, circuit_counts = get_labels_statistic(
        data_path="data/asi-fuboco-test"
    )
    print("num of subcircuit: ", len(instance_counts.keys()))
    # print(json.dumps(instance_counts, indent=2))
    pd_instance_counts = pd.DataFrame.from_dict(
        instance_counts, orient="index", columns=["instance_counts"]
    )
    pd_circuit_counts = pd.DataFrame.from_dict(
        {k: len(v) for k, v in circuit_counts.items()},
        orient="index",
        columns=["circuit_counts"],
    )
    result = pd.concat([pd_instance_counts, pd_circuit_counts], axis=1, join="inner")

    print(result)

    eval_subcircuits = [
        "MosfetCascodeAnalogInverterTwoCurrentMirrorLoads",
        "MosfetCascodeAnalogInverterNmosDiodeTransistorPmosCurrentMirrorLoad",
    ]
    for sc in eval_subcircuits:
        print(f"Circuits contain `{sc}`: \n")
        print(circuit_counts[sc])

    print("raw subcircuit labels:")
    _, circuit_counts = get_rawlabels_statistic(data_path="data/asi-fuboco-test")
    print(circuit_counts.keys())
