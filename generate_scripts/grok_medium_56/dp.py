import re
from collections import defaultdict


def parse_netlist(netlist):
    """Extract transistor information from the SPICE netlist."""
    transistors = []
    for line in netlist.splitlines():
        match = re.match(
            r"(m\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)", line.strip()
        )
        if match:
            name, drain, gate, source, bulk, type_ = match.groups()
            transistors.append(
                {
                    "name": name,
                    "drain": drain,
                    "gate": gate,
                    "source": source,
                    "bulk": bulk,
                    "type": type_,
                }
            )
    return transistors


def group_by_source(transistors):
    """Group transistors by their source node."""
    source_to_transistors = defaultdict(list)
    for t in transistors:
        source_to_transistors[t["source"]].append(t)
    return source_to_transistors


def find_potential_input_pairs(source_to_transistors):
    """Identify pairs of transistors with same source, different gates, and same type."""
    potential_pairs = []
    for source, trans_list in source_to_transistors.items():
        for i in range(len(trans_list)):
            for j in range(i + 1, len(trans_list)):
                t1 = trans_list[i]
                t2 = trans_list[j]
                if t1["gate"] != t2["gate"] and t1["type"] == t2["type"]:
                    potential_pairs.append((t1, t2))
    return potential_pairs


def find_differential_pairs(potential_pairs, source_to_transistors):
    """Find full differential pairs including input and load/cascode transistors."""
    diff_pairs = []
    for t1, t2 in potential_pairs:
        drain1 = t1["drain"]
        drain2 = t2["drain"]
        if drain1 in source_to_transistors and drain2 in source_to_transistors:
            candidates1 = source_to_transistors[drain1]
            candidates2 = source_to_transistors[drain2]
            for t3 in candidates1:
                for t4 in candidates2:
                    if (
                        t3["gate"] == t4["gate"]
                        and t3["type"] == t4["type"]
                        and t3["name"] != t4["name"]
                    ):
                        diff_pairs.append(
                            [t1["name"], t2["name"], t3["name"], t4["name"]]
                        )
    return diff_pairs


def identify_differential_pairs(netlist):
    """Main function to identify differential pairs in a SPICE netlist."""
    # Step 1: Extract transistor information
    transistors = parse_netlist(netlist)

    # Step 2 & 3: Group by source and identify potential pairs
    source_to_transistors = group_by_source(transistors)
    potential_pairs = find_potential_input_pairs(source_to_transistors)

    # Step 4, 5, 6, 7: Analyze configuration and compile differential pairs
    diff_pairs = find_differential_pairs(potential_pairs, source_to_transistors)

    # Format the result
    result = []
    for pair in diff_pairs:
        result.append({"sub_circuit_name": "DiffPair", "transistor_names": pair})
    return result


# Example usage with the test case
if __name__ == "__main__":
    netlist = """
    c1 a out
    m1 b ibias ground ground nmos
    m2 c ibias ground ground nmos
    m3 d ibias ground ground nmos
    m4 e b supply supply pmos
    m5 f e g g nmos
    m6 a e h h nmos
    m7 f d i i pmos
    m8 i f supply supply pmos
    m9 a d j j pmos
    m10 j f supply supply pmos
    m11 k ibias ground ground nmos
    m12 g in1 k k nmos
    m13 h in2 k k nmos
    c2 out ground
    m14 out a ground ground nmos
    m15 out c l l pmos
    m16 l l supply supply pmos
    m17 e e k k nmos
    m18 ibias ibias ground ground nmos
    m19 b b supply supply pmos
    m20 c c m m pmos
    m21 m l supply supply pmos
    m22 d d supply supply pmos
    """
    diff_pairs = identify_differential_pairs(netlist)
    print(diff_pairs)
