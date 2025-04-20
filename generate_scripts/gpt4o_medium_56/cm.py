import re
from collections import defaultdict
from itertools import combinations


def parse_netlist(netlist_str):
    mosfets = {}
    lines = netlist_str.strip().split("\n")
    for line in lines:
        if line.startswith("m"):
            parts = line.split()
            name = parts[0]
            drain, gate, source, bulk, model = parts[1:6]
            if model in ["nmos", "pmos"]:
                mosfets[name] = {
                    "name": name,
                    "drain": drain,
                    "gate": gate,
                    "source": source,
                    "bulk": bulk,
                    "type": model,
                }
    return mosfets


def group_by_gate_and_type(mosfets):
    groups = defaultdict(list)
    for m in mosfets.values():
        key = (m["gate"], m["type"])
        groups[key].append(m)
    return groups


def find_shared_connection_groups(group, connection_key):
    conn_map = defaultdict(list)
    for m in group:
        conn_map[m[connection_key]].append(m)
    return [group for group in conn_map.values() if len(group) > 1]


def is_connected_to_supply_or_ground(node):
    return node.lower() in ["ground", "supply"]


def find_current_mirrors(mosfets):
    mirrors = []
    grouped_by_gate = group_by_gate_and_type(mosfets)

    for (gate, type_), group in grouped_by_gate.items():
        # Step 4: Check for shared drain or source
        shared_drain_groups = find_shared_connection_groups(group, "drain")
        shared_source_groups = find_shared_connection_groups(group, "source")
        potential_mirrors = shared_drain_groups + shared_source_groups

        for mirror_group in potential_mirrors:
            names = [m["name"] for m in mirror_group]
            # Step 5: Check source to ground/supply for at least one
            if any(is_connected_to_supply_or_ground(m["source"]) for m in mirror_group):
                mirrors.append(
                    {"sub_circuit_name": "CM", "transistor_names": sorted(names)}
                )
    # Remove duplicates (based on transistor set)
    unique_mirrors = []
    seen = set()
    for mirror in mirrors:
        key = tuple(sorted(mirror["transistor_names"]))
        if key not in seen:
            unique_mirrors.append(mirror)
            seen.add(key)
    return unique_mirrors


# === TEST CASE ===
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

# mosfets = parse_netlist(netlist)
# mirrors = find_current_mirrors(mosfets)

# import pprint

# pprint.pprint(mirrors)
