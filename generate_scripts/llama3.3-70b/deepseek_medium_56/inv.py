import sys
from collections import defaultdict


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


def trace_pmos_path(mosfet, transistors_dict, visited=None):
    if visited is None:
        visited = set()
    if mosfet["name"] in visited:
        return []
    visited.add(mosfet["name"])
    path = [mosfet]
    if mosfet["source"] == "supply":
        return path
    next_source = mosfet["source"]
    for t in transistors_dict.values():
        if (
            t["model_type"] == "pmos"
            and t["drain"] == next_source
            and t["name"] not in visited
        ):
            sub_path = trace_pmos_path(t, transistors_dict, visited)
            if sub_path:
                return path + sub_path
    if next_source == "supply":
        return path
    return []


def trace_nmos_path(mosfet, transistors_dict, visited=None):
    if visited is None:
        visited = set()
    if mosfet["name"] in visited:
        return []
    visited.add(mosfet["name"])
    path = [mosfet]
    if mosfet["source"] == "ground":
        return path
    next_source = mosfet["source"]
    for t in transistors_dict.values():
        if (
            t["model_type"] == "nmos"
            and t["drain"] == next_source
            and t["name"] not in visited
        ):
            sub_path = trace_nmos_path(t, transistors_dict, visited)
            if sub_path:
                return path + sub_path
    if next_source == "ground":
        return path
    return []


def find_inverters(netlist):
    transistors = parse_netlist(netlist)
    transistors_dict = {t["name"]: t for t in transistors}
    grouped = defaultdict(list)
    for t in transistors:
        grouped[t["drain"]].append(t)

    inverters = []
    for drain, group in grouped.items():
        pmos_members = []
        for t in group:
            if t["model_type"] == "pmos":
                path = trace_pmos_path(t, transistors_dict)
                if path:
                    pmos_members.extend(path)

        nmos_members = []
        for t in group:
            if t["model_type"] == "nmos":
                path = trace_nmos_path(t, transistors_dict)
                if path:
                    nmos_members.extend(path)

        if pmos_members and nmos_members:
            all_transistors = pmos_members + nmos_members
            unique_names = list({t["name"] for t in all_transistors})
            sorted_names = sorted(unique_names, key=lambda x: int(x[1:]))
            inverters.append(
                {"sub_circuit_name": "Inverter", "transistor_names": sorted_names}
            )

    return inverters


if __name__ == "__main__":
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
    inverters = find_inverters(input_netlist)
    print(inverters)
