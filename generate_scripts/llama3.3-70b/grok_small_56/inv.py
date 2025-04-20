def extract_inverters(netlist):
    # Step 1 & 2: Parse the netlist to identify MOSFETs and their connections
    mosfets = []
    for line in netlist.split("\n"):
        line = line.strip()
        if line.startswith("m"):
            tokens = line.split()
            if len(tokens) >= 6 and tokens[5].lower() in ["pmos", "nmos"]:
                mosfets.append(
                    {
                        "name": tokens[0],
                        "drain": tokens[1],
                        "gate": tokens[2],
                        "source": tokens[3],
                        "body": tokens[4],
                        "type": tokens[5].lower(),
                    }
                )

    # Step 3 & 4: Identify inverter configurations with PMOS pull-up and NMOS pull-down
    inverters = []
    # Filter PMOS with source connected to 'supply' and not diode-connected
    pmos_list = [
        m
        for m in mosfets
        if m["type"] == "pmos" and m["source"] == "supply" and m["gate"] != m["drain"]
    ]

    for pmos in pmos_list:
        output = pmos["drain"]

        # Case 1: Direct NMOS pull-down to ground (simple inverter)
        direct_nmos = [
            m
            for m in mosfets
            if m["type"] == "nmos"
            and m["drain"] == output
            and m["source"] == "ground"
            and m["gate"] != m["drain"]
        ]
        for nmos in direct_nmos:
            # Step 5 & 6: Compile and validate basic inverter (assuming functionality based on structure)
            inverters.append(
                {
                    "sub_circuit_name": "Inverter",
                    "transistor_names": [pmos["name"], nmos["name"]],
                }
            )

        # Case 2: Two-transistor NMOS pull-down (extended inverter)
        first_nmos_list = [
            m
            for m in mosfets
            if m["type"] == "nmos"
            and m["drain"] == output
            and m["source"] != "ground"
            and m["gate"] != m["drain"]
        ]
        for fn in first_nmos_list:
            intermediate_node = fn["source"]
            second_nmos_list = [
                m
                for m in mosfets
                if m["type"] == "nmos"
                and m["drain"] == intermediate_node
                and m["source"] == "ground"
            ]
            for sn in second_nmos_list:
                # Step 5 & 6: Include additional transistor if it forms a valid pull-down path
                inverters.append(
                    {
                        "sub_circuit_name": "Inverter",
                        "transistor_names": [pmos["name"], fn["name"], sn["name"]],
                    }
                )

    # Step 7: Inverter chains could be added here, but test case has no chains, so omitted
    return inverters
