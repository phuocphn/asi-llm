def identify_current_mirrors(netlist):
    # Parse all MOSFETs
    mosfets = []
    for line in netlist.split("\n"):
        line = line.strip()
        if not line or not line.startswith("m"):
            continue
        parts = line.split()
        name = parts[0]
        drain = parts[1]
        gate = parts[2]
        source = parts[3]
        model = parts[4].lower() if parts[4].lower() in ["pmos", "nmos"] else None
        if not model:
            continue
        mosfets.append(
            {
                "name": name,
                "drain": drain,
                "gate": gate,
                "source": source,
                "model": model,
            }
        )

    # Group by model and gate
    groups = {}
    for mosfet in mosfets:
        key = (mosfet["model"], mosfet["gate"])
        if key not in groups:
            groups[key] = []
        groups[key].append(mosfet)

    # Filter groups based on source connection and size
    current_mirrors = []
    for key, group in groups.items():
        model_type = key[0]
        valid = True
        # Check if all sources are correct
        for mosfet in group:
            if model_type == "pmos" and mosfet["source"] != "supply":
                valid = False
                break
            if model_type == "nmos" and mosfet["source"] != "ground":
                valid = False
                break
        if not valid or len(group) < 2:
            continue
        # Collect transistor names
        transistor_names = sorted([m["name"] for m in group], key=lambda x: int(x[1:]))
        current_mirrors.append(
            {"sub_circuit_name": "CM", "transistor_names": transistor_names}
        )

    # Sort the list by the first transistor name for consistent order (optional)
    current_mirrors.sort(key=lambda x: x["transistor_names"][0])
    return current_mirrors


# Test case
input_netlist = """
c1 a out
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
m18 ibias ibias supply supply pmos
"""

output = identify_current_mirrors(input_netlist)
print(output)
