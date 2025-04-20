#!/usr/bin/env python3
"""
find_diff_pairs.py

A script to parse a SPICE netlist and identify differential transistor pairs along with their current-mirror or load partners.

Usage:
    python find_diff_pairs.py <netlist_file>

Output:
    A JSON list of detected differential pairs, each as a dict with keys:
      - sub_circuit_name: name assigned to the diff pair ("DiffPair")
      - transistor_names: list of transistor instance names in the pair and their loads
"""
import sys
import json
from collections import defaultdict


def parse_netlist(path):
    """
    Parse a SPICE netlist, extracting transistor instances.
    Returns a list of dicts, each with keys: name, drain, gate, source, body, type.
    """
    transistors = []
    with open(path) as f:
        for line in f:
            # strip comments and whitespace
            line = line.strip()
            if not line or line.startswith("*"):
                continue
            tokens = line.split()
            # transistor lines start with 'm' or 'M'
            if tokens[0][0].lower() == "m" and len(tokens) >= 6:
                name = tokens[0]
                drain, gate, source, body = tokens[1:5]
                model = tokens[5].lower()
                transistors.append(
                    {
                        "name": name,
                        "drain": drain,
                        "gate": gate,
                        "source": source,
                        "body": body,
                        "type": model,
                    }
                )
    return transistors


def find_diff_pairs(transistors):
    """
    Identify differential pairs and their load mirror partners.
    Returns a list of dicts with sub_circuit_name and transistor_names.
    """
    # index by transistor type for quick lookup
    by_type = defaultdict(list)
    for t in transistors:
        by_type[t["type"]].append(t)

    diff_pairs = []
    # consider each type separately
    for typ, tlist in by_type.items():
        # find input pairs: same source, different gates
        for i in range(len(tlist)):
            for j in range(i + 1, len(tlist)):
                t1, t2 = tlist[i], tlist[j]
                if t1["source"] == t2["source"] and t1["gate"] != t2["gate"]:
                    # candidate input pair
                    s_node = t1["source"]
                    # find load pairs among same type
                    loads = []
                    for l1 in tlist:
                        for l2 in tlist:
                            if l1["name"] >= l2["name"]:
                                continue
                            # loads share gate and feed from input drains
                            if (
                                l1["gate"] == l2["gate"]
                                and l1["source"] == t1["drain"]
                                and l2["source"] == t2["drain"]
                            ):
                                loads.append((l1, l2))
                    for l1, l2 in loads:
                        names = [t1["name"], t2["name"], l1["name"], l2["name"]]
                        diff_pairs.append(
                            {"sub_circuit_name": "DiffPair", "transistor_names": names}
                        )
    return diff_pairs


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <netlist_file>", file=sys.stderr)
        sys.exit(1)
    netlist_file = sys.argv[1]
    transistors = parse_netlist(netlist_file)
    diff_pairs = find_diff_pairs(transistors)
    print(json.dumps(diff_pairs, indent=2))


if __name__ == "__main__":
    main()
