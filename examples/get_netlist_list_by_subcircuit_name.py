import glob
import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict


def get_netlist_list_by_subcircuit_names(data_path="data/benchmark-asi-100-train"):
    # all_subcircuits = set()
    subcircuit_netlist_map = defaultdict(set)
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
                subcircuit_netlist_map[circuit_name].add(netlist_dir)

    return subcircuit_netlist_map


if __name__ == "__main__":
    """Get list of netlist contains particular subcircuit name"""

    netlist_subcircuit_map = get_netlist_list_by_subcircuit_names(
        data_path="data/asi-fuboco-train"
    )
    print("num of subcircuit: ", len(netlist_subcircuit_map.keys()))
    print(json.dumps({k: len(v) for k, v in netlist_subcircuit_map.items()}, indent=2))

    print("Circuits contain `MosfetCascodeAnalogInverterTwoCurrentMirrorLoads`: \n")
    print(netlist_subcircuit_map["MosfetCascodeAnalogInverterTwoCurrentMirrorLoads"])

    print(
        "Circuits contain `MosfetCascodeAnalogInverterNmosDiodeTransistorPmosCurrentMirrorLoad`: \n"
    )
    print(
        netlist_subcircuit_map[
            "MosfetCascodeAnalogInverterNmosDiodeTransistorPmosCurrentMirrorLoad"
        ]
    )
