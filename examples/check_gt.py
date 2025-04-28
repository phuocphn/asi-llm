from src.netlist import SPICENetlist
from collections import defaultdict

import glob

# hl2_subcircuit_names = {'DiffPair', 'CM', 'Inverter'}


def check_hl2_ground_truth_correctness():
    subcircuit_names = []

    for dir in ["small", "medium", "large"]:
        for i in range(1, 101):
            try:
                data = SPICENetlist(f"data/benchmark-asi-100/{dir}/{i}/")
                print(f"dir={dir}, i={i}")
                print(data.hl2_gt)
                for sub_circuit in data.hl2_gt:
                    if sub_circuit["sub_circuit_name"] not in subcircuit_names:
                        subcircuit_names.append(sub_circuit["sub_circuit_name"])

                    if len(sub_circuit["transistor_names"]) < 2:
                        print(
                            f"found {len(sub_circuit['transistor_names'])} transistors in {sub_circuit['sub_circuit_name']} "
                            + "dir: "
                            + f"data/benchmark-asi-100/{dir}/{i}/"
                        )
                        exit(1)

            except Exception as e:
                print(f"error: {e}")
                continue

    print("checking ground truth correctness...")
    print("non-standard names:")

    subcircuit_names = list(set(subcircuit_names))
    assert (
        len(subcircuit_names) == 3
    ), f"found {len(subcircuit_names)} subcircuit names: {subcircuit_names}"
    assert "Inverter" in subcircuit_names
    assert "CM" in subcircuit_names
    assert "DiffPair" in subcircuit_names
    print(subcircuit_names)
    print("all subcircuit names are correct")

    print("done")


def check_hl3_ground_truth_correctness():
    subcircuit_names = []
    subcircuit_counts = defaultdict(list)
    for dir in ["small", "medium", "large"]:
        for i in range(1, 101):
            try:
                data = SPICENetlist(f"data/asi-fuboco-test/{dir}/{i}/")
                print(f"dir={dir}, i={i}")
                print(data.hl3_gt)
                for sub_circuit in data.hl3_gt:
                    subcircuit_counts[sub_circuit["sub_circuit_name"]].append(i)
                    # if sub_circuit["sub_circuit_name"] not in subcircuit_names:
                    # subcircuit_names.append(sub_circuit["sub_circuit_name"])

            except Exception as e:
                print(f"error: {e}")
                continue

    print("checking ground truth correctness...")
    subcircuit_counts = {k: len(v) for k, v in subcircuit_counts.items()}
    print(subcircuit_counts)
    print("all subcircuit names are correct")

    print("done")


check_hl3_ground_truth_correctness()
