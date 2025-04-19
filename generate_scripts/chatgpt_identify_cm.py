import re
from collections import defaultdict


def parse_mosfets(netlist_lines):
    mosfets = []
    for line in netlist_lines:
        if line.lower().startswith("m"):
            parts = line.strip().split()
            name = parts[0]
            drain, gate, source, bulk = parts[1:5]
            mtype = parts[5].lower()  # either 'nmos' or 'pmos'
            mosfets.append(
                {
                    "name": name,
                    "drain": drain,
                    "gate": gate,
                    "source": source,
                    "bulk": bulk,
                    "type": mtype,
                }
            )
    return mosfets


def find_shared_gate_groups(mosfets):
    gate_groups = defaultdict(list)
    for m in mosfets:
        gate_groups[m["gate"]].append(m)
    return [group for group in gate_groups.values() if len(group) > 1]


def find_diode_connected(mosfets):
    return [m for m in mosfets if m["drain"] == m["gate"]]


def find_matching_transistors(group):
    matches = []
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            a, b = group[i], group[j]
            if (
                a["type"] == b["type"]
                and {a["source"], a["bulk"]} == {b["source"], b["bulk"]}
                and a["gate"] == b["gate"]
            ):
                matches.append((a, b))
    return matches


def find_current_mirrors(mosfets):
    mirrors = []
    gate_groups = find_shared_gate_groups(mosfets)
    diode_conns = find_diode_connected(mosfets)
    used = set()

    for group in gate_groups:
        group_names = {m["name"] for m in group}
        if group_names & used:
            continue

        matching_pairs = find_matching_transistors(group)
        if not matching_pairs:
            continue

        # Include diode connected if it's part of the group
        diode_in_group = [m for m in group if m in diode_conns]
        if diode_in_group:
            group_set = set(m["name"] for m in group)
            mirrors.append(
                {"sub_circuit_name": "CM", "transistor_names": sorted(group_set)}
            )
            used.update(group_set)

    # Handle biasing group separately
    possible_bias_group = [
        m for m in mosfets if m["gate"] == m["drain"] and m["source"] == m["bulk"]
    ]
    bias_groups = defaultdict(list)
    for m in possible_bias_group:
        key = (m["gate"], m["source"], m["type"])
        bias_groups[key].append(m)
    for group in bias_groups.values():
        if len(group) > 1:
            names = [m["name"] for m in group]
            if not (set(names) & used):
                mirrors.append(
                    {"sub_circuit_name": "CM", "transistor_names": sorted(names)}
                )
                used.update(names)
    return mirrors


# --- Test Case ---

netlist = """
c1 a out
c2 b out
m1 c d ground ground nmos
m2 e d ground ground nmos
m3 f d ground ground nmos
m4 d ibias supply supply pmos
m5 g ibias supply supply pmos
m6 h h i i nmos
m7 i i ground ground nmos
m8 a h j j nmos
m9 j i ground ground nmos
m10 k ibias supply supply pmos
m11 h in1 k k pmos
m12 a in2 k k pmos
m13 out b ground ground nmos
m14 out c l l pmos
m15 l l supply supply pmos
c3 out ground
m16 m a ground ground nmos
m17 m e n n pmos
m18 n n supply supply pmos
m19 b g o o nmos
m20 o m ground ground nmos
m21 b f p p pmos
m22 p ibias supply supply pmos
m23 d d ground ground nmos
m24 g g ground ground nmos
m25 c c q q pmos
m26 q l supply supply pmos
m27 e e r r pmos
m28 r n supply supply pmos
m29 f f supply supply pmos
m30 ibias ibias supply supply pmos
""".strip().split(
    "\n"
)

mosfets = parse_mosfets(netlist)
result = find_current_mirrors(mosfets)

# Output results
import json

print(json.dumps(result, indent=2))
