import sys
from itertools import combinations


def parse_netlist(netlist):
    transistors = []
    lines = netlist.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        if parts[0].startswith("m"):
            name = parts[0]
            drain = parts[1]
            gate = parts[2]
            source = parts[3]
            bulk = parts[4]
            model_type = parts[5]
            transistors.append(
                {
                    "name": name,
                    "drain": drain,
                    "gate": gate,
                    "source": source,
                    "bulk": bulk,
                    "model_type": model_type,
                }
            )
    return transistors


def is_valid_pair(t1, t2, transistors):
    if t1["model_type"] != t2["model_type"]:
        return False
    if t1["source"] != t2["source"]:
        return False
    if t1["gate"] == t2["gate"]:
        return False
    required_type = "nmos" if t1["model_type"] == "pmos" else "pmos"
    drain1 = t1["drain"]
    has_opposite_drain1 = any(
        t
        for t in transistors
        if t["name"] not in {t1["name"], t2["name"]}
        and t["model_type"] == required_type
        and t["drain"] == drain1
    )
    drain2 = t2["drain"]
    has_opposite_drain2 = any(
        t
        for t in transistors
        if t["name"] not in {t1["name"], t2["name"]}
        and t["model_type"] == required_type
        and t["drain"] == drain2
    )
    return has_opposite_drain1 and has_opposite_drain2


def find_differential_pairs(netlist):
    transistors = parse_netlist(netlist)
    differential_pairs = []
    for t1, t2 in combinations(transistors, 2):
        if is_valid_pair(t1, t2, transistors):
            names = sorted([t1["name"], t2["name"]], key=lambda x: int(x[1:]))
            entry = {"sub_circuit_name": "DiffPair", "transistor_names": names}
            differential_pairs.append(entry)
    return differential_pairs


if __name__ == "__main__":
    input_netlist = """c1 a out
c2 b out
m1 c ibias supply supply pmos
m2 d ibias supply supply pmos
m3 e f ground ground nmos
m4 a e f f nmos
m5 f f ground ground nmos
m6 g ibias supply supply pmos
m7 e in1 g g pmos
m8 a in2 g g pmos
m9 out c h h nmos
m10 h d ground ground nmos
m11 out b supply supply pmos
c3 out ground
m12 i d ground ground nmos
m13 i a supply supply pmos
m14 b i ground ground nmos
m15 b ibias supply supply pmos
m16 c c ground ground nmos
m17 d d ground ground nmos
m18 ibias ibias supply supply pmos"""
    pairs = find_differential_pairs(input_netlist)
    print(pairs)
