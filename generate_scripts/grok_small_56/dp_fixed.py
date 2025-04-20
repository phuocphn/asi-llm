def parse_netlist(netlist):
    """Parse the netlist and extract transistor information."""
    transistors = []
    lines = netlist.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("m"):
            tokens = line.split()
            if (
                len(tokens) >= 6
            ):  # Ensure enough tokens: name drain gate source bulk type
                transistor = {
                    "name": tokens[0],
                    "drain": tokens[1],
                    "gate": tokens[2],
                    "source": tokens[3],
                    "bulk": tokens[4],
                    "type": tokens[5],
                }
                transistors.append(transistor)
    print("Parsed transistors:", [t["name"] for t in transistors])
    return transistors


def find_differential_pairs(transistors):
    """Find differential pairs among PMOS transistors."""
    # Separate PMOS transistors
    pmos_transistors = [t for t in transistors if t["type"].lower() == "pmos"]
    print("PMOS transistors:", [t["name"] for t in pmos_transistors])

    # Group by source node
    source_to_trans = {}
    for t in pmos_transistors:
        source = t["source"]
        if source not in source_to_trans:
            source_to_trans[source] = []
        source_to_trans[source].append(t)
    print(
        "Source to transistors:",
        {k: [t["name"] for t in v] for k, v in source_to_trans.items()},
    )

    # Find pairs with same source and different gates
    diff_pairs = []
    from itertools import combinations

    for source, trans_list in source_to_trans.items():
        if len(trans_list) >= 2:
            for t1, t2 in combinations(trans_list, 2):
                print(
                    f"Considering pair: {t1['name']} (gate: {t1['gate']}), {t2['name']} (gate: {t2['gate']})"
                )
                if t1["gate"] != t2["gate"]:
                    pair = {
                        "transistor1": t1["name"],
                        "transistor2": t2["name"],
                        "source": source,
                        "gate1": t1["gate"],
                        "gate2": t2["gate"],
                        "drain1": t1["drain"],
                        "drain2": t2["drain"],
                    }
                    diff_pairs.append(pair)
                    print(f"Accepted pair: {t1['name']}, {t2['name']}")

    return diff_pairs


# Test with full netlist
full_netlist = """c1 a out
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

# Parse and find pairs
transistors = parse_netlist(full_netlist)
diff_pairs = find_differential_pairs(transistors)

print(diff_pairs)

# Output results
# print("\nDifferential pairs found:")
# for pair in diff_pairs:
#     print(f"Pair: {pair['transistor1']} and {pair['transistor2']}")
#     print(f"  Source: {pair['source']}")
#     print(f"  Gates: {pair['gate1']}, {pair['gate2']}")
#     print(f"  Drains: {pair['drain1']}, {pair['drain2']}")

# # Test with minimal netlist
# minimal_netlist = "m9 e in1 f f pmos\nm10 a in2 f f pmos"
# print("\nTesting minimal netlist:")
# transistors_min = parse_netlist(minimal_netlist)
# diff_pairs_min = find_differential_pairs(transistors_min)
# for pair in diff_pairs_min:
#     print(f"Pair: {pair['transistor1']} and {pair['transistor2']}")
