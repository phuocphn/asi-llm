def find_differential_pairs(netlist):
    transistors = {}
    lines = netlist.strip().split("\n")
    for line in lines:
        line = line.split("*")[0].strip()  # Remove comments
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        if parts[0].startswith("m") and len(parts) >= 6:
            name = parts[0]
            drain = parts[1]
            gate = parts[2]
            source = parts[3]
            model = parts[5]
            transistors[name] = {
                "drain": drain,
                "gate": gate,
                "source": source,
                "model": model,
            }

    diff_pairs = []
    processed_groups = set()

    # Generate all possible pairs of transistors
    transistor_names = list(transistors.keys())
    for i in range(len(transistor_names)):
        for j in range(i + 1, len(transistor_names)):
            a = transistor_names[i]
            b = transistor_names[j]
            a_info = transistors[a]
            b_info = transistors[b]

            # Check if they are same model and source, different gates
            if a_info["model"] != b_info["model"]:
                continue
            if a_info["source"] != b_info["source"]:
                continue
            if a_info["gate"] == b_info["gate"]:
                continue

            # Find possible load transistors
            a_drain = a_info["drain"]
            b_drain = b_info["drain"]
            candidates_c = []
            candidates_d = []
            for name, info in transistors.items():
                if name == a or name == b:
                    continue
                if info["source"] == a_drain:
                    candidates_c.append(name)
                if info["source"] == b_drain:
                    candidates_d.append(name)

            # Check for load pairs (c, d)
            found = False
            for c in candidates_c:
                for d in candidates_d:
                    if c == d:
                        continue
                    c_info = transistors[c]
                    d_info = transistors[d]
                    if c_info["model"] != d_info["model"]:
                        continue
                    if c_info["gate"] != d_info["gate"]:
                        continue
                    # Found a valid load pair
                    group = sorted([a, b, c, d])
                    group_set = frozenset(group)
                    if group_set not in processed_groups:
                        diff_pairs.append(
                            {"sub_circuit_name": "DiffPair", "transistor_names": group}
                        )
                        processed_groups.add(group_set)
                    found = True
                    break
                if found:
                    break

    return diff_pairs


# Example usage
input_netlist = """
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

# result = find_differential_pairs(input_netlist)
# print(result)
