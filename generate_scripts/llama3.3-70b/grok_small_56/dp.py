import re
from collections import defaultdict
from itertools import combinations


def get_transistor_number(name):
    return int(name[1:])  # Extract numerical part after 'm' for sorting


def find_differential_pairs_v0(netlist):
    # Split netlist into lines and extract transistor data
    lines = netlist.strip().split("\n")
    transistors = []
    for line in lines:
        if line.startswith("m"):
            tokens = line.split()
            if len(tokens) >= 6:
                name = tokens[0]
                drain = tokens[1]
                gate = tokens[2]
                source = tokens[3]
                substrate = tokens[4]
                type_ = tokens[5].lower()
                if type_ in ["nmos", "pmos"]:
                    transistors.append(
                        {
                            "name": name,
                            "drain": drain,
                            "gate": gate,
                            "source": source,
                            "substrate": substrate,
                            "type": type_,
                        }
                    )

    # Separate transistors by type
    nmos_transistors = [t for t in transistors if t["type"] == "nmos"]
    pmos_transistors = [t for t in transistors if t["type"] == "pmos"]

    # Function to find differential pairs within a transistor list
    def find_pairs(transistor_list):
        # Group transistors by source node
        source_to_trans = defaultdict(list)
        for t in transistor_list:
            source_to_trans[t["source"]].append(t)

        # Identify pairs with same source and different gates
        pairs = []
        for source, trans_list in source_to_trans.items():
            if len(trans_list) >= 2:
                for pair in combinations(trans_list, 2):
                    if pair[0]["gate"] != pair[1]["gate"]:
                        pair_names = [pair[0]["name"], pair[1]["name"]]
                        pair_names.sort(key=get_transistor_number)
                        pairs.append(pair_names)
        return pairs

    # Find pairs for NMOS and PMOS
    nmos_pairs = find_pairs(nmos_transistors)
    pmos_pairs = find_pairs(pmos_transistors)

    # Combine all identified pairs
    all_pairs = nmos_pairs + pmos_pairs

    # Format output as list of dictionaries
    output = [
        {"sub_circuit_name": "DiffPair", "transistor_names": pair} for pair in all_pairs
    ]
    return output


from collections import defaultdict
from itertools import combinations


def get_transistor_number(name):
    return int(name[1:])


def find_pairs(transistors):
    source_to_trans = defaultdict(list)
    for t in transistors:
        source_to_trans[t["source"]].append(t)
    pairs = []
    for source, trans_list in source_to_trans.items():
        if len(trans_list) >= 2:
            for pair in combinations(trans_list, 2):
                if pair[0]["gate"] != pair[1]["gate"]:
                    pair_names = [pair[0]["name"], pair[1]["name"]]
                    pair_names.sort(key=get_transistor_number)
                    pairs.append(pair_names)
    return pairs


def find_differential_pairs(netlist):
    lines = netlist.strip().split("\n")
    transistors = []
    for line in lines:
        if line.startswith("m"):
            tokens = line.split()
            if len(tokens) >= 6:
                name, drain, gate, source, substrate, type_ = (
                    tokens[0],
                    tokens[1],
                    tokens[2],
                    tokens[3],
                    tokens[4],
                    tokens[5].lower(),
                )
                if type_ in ["nmos", "pmos"]:
                    transistors.append(
                        {
                            "name": name,
                            "drain": drain,
                            "gate": gate,
                            "source": source,
                            "type": type_,
                        }
                    )

    nmos_transistors = [t for t in transistors if t["type"] == "nmos"]
    pmos_transistors = [t for t in transistors if t["type"] == "pmos"]

    nmos_pairs = find_pairs(nmos_transistors)
    pmos_pairs = find_pairs(pmos_transistors)
    all_pairs = nmos_pairs + pmos_pairs

    return [
        {"sub_circuit_name": "DiffPair", "transistor_names": pair} for pair in all_pairs
    ]


# Example usage with the test case
if __name__ == "__main__":
    netlist = """c1 a out
    m1 b c supply supply pmos
    m2 d c supply supply pmos
    m3 e e supply supply pmos
    m4 a e supply supply pmos
    m5 e d ground ground nmos
    m6 a d ground ground nmos
    m7 f ibias c c pmos
    m8 c c supply supply pmos
    m9 e in1 f f pmos
    m10 a in2 f f pmos
    c2 out ground
    m11 out b g g nmos
    m12 g g ground ground nmos
    m13 out a supply supply pmos
    m14 b b h h nmos
    m15 h g ground ground nmos
    m16 d d ground ground nmos
    m17 ibias ibias i i pmos
    m18 i c supply supply pmos"""
    # netlist = "m9 e in1 f f pmos\nm10 a in2 f f pmos"
    result = find_differential_pairs(netlist)
    print(result)
