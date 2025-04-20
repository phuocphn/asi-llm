import glob
import os
import xml.etree.ElementTree as ET


def get_all_subcircuit_names(data_path="data/benchmark-asi-100-train"):
    all_subcircuits = set()
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
                all_subcircuits.add(circuit_name)

    return all_subcircuits


if __name__ == "__main__":
    """Check lablels in train set and test set are identical"""

    subcircuit_names_train = get_all_subcircuit_names(data_path="data/asi-fuboco-train")
    print(subcircuit_names_train)
    print(len(subcircuit_names_train))

    subcircuit_names_test = get_all_subcircuit_names(data_path="data/asi-fuboco-test")
    print(subcircuit_names_test)
    print(len(subcircuit_names_test))

    # assert subcircuit_names_test == subcircuit_names_train
    for sc in subcircuit_names_test:
        if sc not in subcircuit_names_train:
            print("benchmark train does not contain: ", sc)

    for sc in subcircuit_names_train:
        if sc not in subcircuit_names_test:
            print("benchmark test does not contain: ", sc)
