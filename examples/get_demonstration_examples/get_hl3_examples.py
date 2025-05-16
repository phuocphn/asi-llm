import glob
import os
import xml.etree.ElementTree as ET
from src.netlist import SPICENetlist


def check_add(list_subcircuits, counter):
    """Check if any of the subcircuits in could be used as demonstration circuits."""
    should_add = False
    for sc in list_subcircuits:
        if sc in counter and counter[sc] == 0:
            counter[sc] = 1
            should_add = True
    return should_add


def get_demonstration_examples(samples):
    all_examples = []
    available_subcircuit_names = [
        "firstStage",
        "secondStage",
        "thirdStage",
        "loadPart",
        "biasPart",
        "feedBack",
    ]
    counter = {k: 0 for k in available_subcircuit_names}

    for index, i in enumerate(samples):
        dir = "small"
        netlist_dir = f"data/asi-fuboco-train/{dir}/{i}/"
        data = SPICENetlist(netlist_dir)

        all_subcircuits = []
        for circuit_name, _ in data.hl3_gt:
            all_subcircuits.append(circuit_name)

        if check_add(all_subcircuits, counter):
            all_examples.append(netlist_dir)

    return all_examples


def check_cover(examples):
    available_subcircuit_names = [
        "firstStage",
        "secondStage",
        "thirdStage",
        "loadPart",
        "biasPart",
        "feedBack",
    ]
    counter = {k: 0 for k in available_subcircuit_names}

    for ex in examples:
        data = SPICENetlist(ex)

        all_subcircuits = []
        for circuit_name, _ in data.hl3_gt:
            all_subcircuits.append(circuit_name)
            counter[circuit_name] = 1

    print(counter)
    return 0 not in counter.values()


if __name__ == "__main__":
    import random

    for _ in range(20000):
        # samples = [56, 49, 51]  # random.sample(range(1, 101), 3)
        samples = random.sample(range(1, 101), 2)
        demonstration_examples = get_demonstration_examples(samples)
        cover = check_cover(demonstration_examples)
        print(f" samples: {samples} ")
        if cover:
            print("found")
            print(len(demonstration_examples), cover)
            print(samples)
            print(demonstration_examples)
            break
