from src.netlist import SPICENetlist
import glob
import re
import json
from calc1 import compute_cluster_metrics, average_metrics
from typing import List, Tuple, Dict, Set, Any
from collections import defaultdict, deque, Counter
import itertools


def findSubCircuitHL1(netlist: str):
    """
    Find all diode-connected transistors and load/compensation capacitors subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """

    # Split the netlist into lines
    return []
    lines = netlist.strip().split("\n")

    # Initialize empty lists to store diode-connected transistors, load capacitors, and compensation capacitors
    diode_connected_transistors = []
    load_capacitors = []
    compensation_capacitors = []

    # Iterate over each line in the netlist
    for line in lines:
        # Split the line into components
        components = line.split()

        # Check if the component is a transistor
        if components[0].startswith("m"):
            # Extract the transistor name and its connections
            transistor_name = components[0]
            drain_node = components[2]
            gate_node = components[3]

            # Check if the transistor is diode-connected (drain and gate nodes are connected to the same node)
            if drain_node == gate_node:
                diode_connected_transistors.append(transistor_name)

        # Check if the component is a capacitor
        elif components[0].startswith("c"):
            # Extract the capacitor name and its connections
            capacitor_name = components[0]
            node1 = components[1]
            node2 = components[2]

            # Check if the capacitor is connected between the output node and ground (load capacitor)
            if node1 == "out" or node2 == "out":
                load_capacitors.append(capacitor_name)
            else:
                compensation_capacitors.append(capacitor_name)

    # Compile the results
    result = []
    if diode_connected_transistors:
        result.append(["MosfetDiode", diode_connected_transistors])
    if load_capacitors:
        result.append(["load_cap", load_capacitors])
    if compensation_capacitors:
        result.append(["compensation_cap", compensation_capacitors])

    return result


def findSubCircuitCM(netlist: str):
    """
    Find all Current Mirrors subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """

    # Split the netlist into lines for easier parsing
    lines = netlist.split("\n")

    # Initialize an empty dictionary to store MOSFETs grouped by their gate connections
    mosfets_by_gate = {}

    # Iterate over each line in the netlist
    for line in lines:
        # Check if the line defines a MOSFET
        if line.startswith("m"):
            # Extract the MOSFET's name and its connections (drain, gate, source, bulk)
            parts = line.split()
            mosfet_name = parts[0]
            gate_connection = parts[2]

            # Add the MOSFET to the appropriate group in the dictionary
            if gate_connection not in mosfets_by_gate:
                mosfets_by_gate[gate_connection] = []
            mosfets_by_gate[gate_connection].append(mosfet_name)

    # Initialize an empty list to store identified current mirrors
    current_mirrors = []

    # Iterate over each group of MOSFETs with shared gates
    for gate, mosfets in mosfets_by_gate.items():
        # Check if there are at least two MOSFETs in the group (minimum for a current mirror)
        if len(mosfets) >= 2:
            # Add the group as a potential current mirror to the list
            current_mirrors.append(["CM", mosfets])

    return current_mirrors


def findSubCircuitDiffPair(netlist: str):
    """
    Find all Differential Pairs in a SPICE netlist.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of lists containing identified differential pairs.
    """

    # Split the netlist into lines for easier parsing
    lines = netlist.splitlines()

    # Initialize an empty list to store transistor information
    transistors = []

    # Iterate over each line in the netlist
    for line in lines:
        # Check if the line describes a transistor (starts with 'm')
        if line.startswith("m"):
            # Extract transistor name and connections from the line
            parts = line.split()
            transistor_name = parts[0]
            connections = parts[1:]

            # Store the transistor information
            transistors.append({"name": transistor_name, "connections": connections})

    # Initialize an empty list to store differential pairs
    differential_pairs = []

    # Iterate over each pair of transistors
    for i in range(len(transistors)):
        for j in range(i + 1, len(transistors)):
            # Check if one transistor is NMOS and the other is PMOS (assuming 'nmos' or 'pmos' is specified in connections)
            if (
                "nmos" in transistors[i]["connections"]
                and "pmos" in transistors[j]["connections"]
            ) or (
                "pmos" in transistors[i]["connections"]
                and "nmos" in transistors[j]["connections"]
            ):
                # Check if the gates of both transistors are connected to the same node
                gate_connection_i = [
                    conn
                    for conn in transistors[i]["connections"]
                    if conn not in ["nmos", "pmos"]
                ]
                gate_connection_j = [
                    conn
                    for conn in transistors[j]["connections"]
                    if conn not in ["nmos", "pmos"]
                ]
                if gate_connection_i[1] == gate_connection_j[1]:
                    # Check for differential pair characteristics (sources connected to the same voltage supply and drains connected to different nodes)
                    source_connection_i = [
                        conn
                        for conn in transistors[i]["connections"]
                        if conn not in ["nmos", "pmos"]
                    ]
                    source_connection_j = [
                        conn
                        for conn in transistors[j]["connections"]
                        if conn not in ["nmos", "pmos"]
                    ]
                    if (
                        source_connection_i[0] == "ground"
                        and source_connection_j[0] == "supply"
                    ) or (
                        source_connection_i[0] == "supply"
                        and source_connection_j[0] == "ground"
                    ):
                        # Check if the drains are connected to different nodes
                        drain_connection_i = [
                            conn
                            for conn in transistors[i]["connections"]
                            if conn not in ["nmos", "pmos"]
                        ]
                        drain_connection_j = [
                            conn
                            for conn in transistors[j]["connections"]
                            if conn not in ["nmos", "pmos"]
                        ]
                        if drain_connection_i[2] != drain_connection_j[2]:
                            # Confirm the differential pair
                            differential_pairs.append(
                                [transistors[i]["name"], transistors[j]["name"]]
                            )

    # Check for additional transistors that might be part of a larger differential pair circuit
    for i in range(len(transistors)):
        for j in range(i + 1, len(transistors)):
            if transistors[i]["connections"][0] == transistors[j]["connections"][0]:
                # Check if both transistors are connected to the same supply voltage (either VDD or GND)
                if (
                    "supply" in transistors[i]["connections"]
                    and "supply" in transistors[j]["connections"]
                ) or (
                    "ground" in transistors[i]["connections"]
                    and "ground" in transistors[j]["connections"]
                ):
                    # Check if the drains are connected to different nodes
                    drain_connection_i = [
                        conn
                        for conn in transistors[i]["connections"]
                        if conn not in ["nmos", "pmos"]
                    ]
                    drain_connection_j = [
                        conn
                        for conn in transistors[j]["connections"]
                        if conn not in ["nmos", "pmos"]
                    ]
                    if drain_connection_i[2] != drain_connection_j[2]:
                        # Confirm the differential pair
                        found = False
                        for pair in differential_pairs:
                            if (
                                transistors[i]["name"] in pair
                                and transistors[j]["name"] in pair
                            ):
                                found = True
                                break
                        if not found:
                            differential_pairs.append(
                                [transistors[i]["name"], transistors[j]["name"]]
                            )

    # Format the output as required
    formatted_output = []
    for pair in differential_pairs:
        formatted_output.append(["DiffPair", pair])

    return formatted_output


def findSubCircuitInverter(netlist: str):
    """
    Find all Inverters subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """

    # Split the netlist into lines for easier parsing
    lines = netlist.split("\n")

    # Initialize an empty list to store the MOSFETs
    mosfets = []

    # Iterate over each line in the netlist
    for line in lines:
        # Check if the line starts with 'm' (indicating a MOSFET)
        if line.strip().startswith("m"):
            # Extract the MOSFET name and its connections
            parts = line.split()
            mosfet_name = parts[0]
            connections = parts[1:]

            # Determine the type of the MOSFET (nmos or pmos)
            mosfet_type = None
            for part in parts:
                if "nmos" in part:
                    mosfet_type = "nmos"
                    break
                elif "pmos" in part:
                    mosfet_type = "pmos"
                    break

            # Add the MOSFET to the list
            mosfets.append(
                {"name": mosfet_name, "type": mosfet_type, "connections": connections}
            )

    # Initialize an empty list to store the inverters
    inverters = []

    # Iterate over each MOSFET
    for i in range(len(mosfets)):
        for j in range(i + 1, len(mosfets)):
            mosfet1 = mosfets[i]
            mosfet2 = mosfets[j]

            # Check if the two MOSFETs are connected in a complementary configuration
            if mosfet1["type"] == "nmos" and mosfet2["type"] == "pmos":
                # Check if their gates are connected to the same node
                if mosfet1["connections"][0] == mosfet2["connections"][0]:
                    # Check if their sources and drains form an inverting path
                    if (
                        mosfet1["connections"][1] == mosfet2["connections"][2]
                        and mosfet1["connections"][2] == mosfet2["connections"][1]
                    ):
                        # Add the inverter to the list
                        inverters.append(
                            ["Inverter", [mosfet1["name"], mosfet2["name"]]]
                        )

    return inverters


def findSubCircuitHL3(netlist: str):
    """
    Find all amplification stages, feedback stages, load and bias parts subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """

    # Split the netlist into lines for easier parsing
    lines = netlist.split("\n")

    # Initialize empty lists to store the transistors for each stage/part
    first_stage_transistors = []
    second_stage_transistors = []
    load_part_transistors = []
    bias_part_transistors = []

    # Iterate over each line in the netlist
    for line in lines:
        # Check if the line defines a transistor (starts with 'm')
        if line.startswith("m"):
            # Extract the transistor name and its connections
            parts = line.split()
            transistor_name = parts[0]
            gate_connection = parts[2]
            drain_connection = parts[3]
            source_connection = parts[4]

            # Identify input transistors (first amplification stage)
            if gate_connection in ["in1", "in2"]:
                first_stage_transistors.append(transistor_name)

            # Determine second amplification stage
            elif gate_connection in [
                t.split()[3]
                for t in lines
                if t.startswith("m") and t.split()[0] in first_stage_transistors
            ]:
                second_stage_transistors.append(transistor_name)

            # Identify load parts
            elif drain_connection in ["supply", "ground"] or source_connection in [
                "supply",
                "ground",
            ]:
                load_part_transistors.append(transistor_name)

            # Determine bias parts
            elif gate_connection == "ibias":
                bias_part_transistors.append(transistor_name)

    # Create the output list with the identified subcircuits and their corresponding transistors
    output = [
        ["firstStage", first_stage_transistors],
        ["secondStage", second_stage_transistors],
        ["loadPart", load_part_transistors],
        ["biasPart", bias_part_transistors],
    ]

    return output


def code_eval(subsets=["small", "medium", "large"]):
    hl1_info = {}
    hl2_info = {}
    hl3_info = {}

    for subset in subsets:
        hl1_results = []
        hl2_results = []
        hl3_results = []

        for i in range(1, 101):
            data = SPICENetlist(f"data/asi-fuboco-test/{subset}/{i}/")

            hl1_results.append(
                compute_cluster_metrics(
                    predicted=findSubCircuitHL1(data.netlist), ground_truth=data.hl1_gt
                )
            )

            cm = findSubCircuitCM(data.netlist)
            dp = findSubCircuitDiffPair(data.netlist)
            invs = findSubCircuitInverter(data.netlist)
            hl2_prediction = cm + dp + invs
            hl2_results.append(
                compute_cluster_metrics(
                    predicted=hl2_prediction, ground_truth=data.hl2_gt
                )
            )

            hl3_results.append(
                compute_cluster_metrics(
                    predicted=findSubCircuitHL3(data.netlist), ground_truth=data.hl3_gt
                )
            )

        hl1_info[subset] = average_metrics(hl1_results)
        hl2_info[subset] = average_metrics(hl2_results)
        hl3_info[subset] = average_metrics(hl3_results)

    return hl1_info, hl2_info, hl3_info


# hl1_info, hl2_info, hl3_info = code_eval()
# print("HL1 Evaluation")
# print("==" * 20)
# print(json.dumps(hl1_info, indent=2))


# print("HL2 Evaluation")
# print("==" * 20)
# print(json.dumps(hl2_info, indent=2))
def prediction(data: SPICENetlist):

    hl1_results = []
    hl2_results = []
    hl3_results = []

    hl1_results.append(
        compute_cluster_metrics(
            predicted=findSubCircuitHL1(data.netlist), ground_truth=data.hl1_gt
        )
    )

    cm = findSubCircuitCM(data.netlist)
    dp = findSubCircuitDiffPair(data.netlist)
    invs = findSubCircuitInverter(data.netlist)
    hl2_prediction = cm + dp + invs
    hl2_results.append(
        compute_cluster_metrics(predicted=hl2_prediction, ground_truth=data.hl2_gt)
    )

    hl3_results.append(
        compute_cluster_metrics(
            predicted=findSubCircuitHL3(data.netlist), ground_truth=data.hl3_gt
        )
    )

    return (
        findSubCircuitHL1(data.netlist),
        hl2_prediction,
        findSubCircuitHL3(data.netlist),
    )


# print("HL3 Evaluation")
# print("==" * 20)
# print(json.dumps(hl3_info, indent=2))
def code_single_eval(data: SPICENetlist):

    hl1_results = []
    hl2_results = []
    hl3_results = []

    hl1_results.append(
        compute_cluster_metrics(
            predicted=findSubCircuitHL1(data.netlist), ground_truth=data.hl1_gt
        )
    )

    cm = findSubCircuitCM(data.netlist)
    dp = findSubCircuitDiffPair(data.netlist)
    invs = findSubCircuitInverter(data.netlist)
    hl2_prediction = cm + dp + invs
    hl2_results.append(
        compute_cluster_metrics(predicted=hl2_prediction, ground_truth=data.hl2_gt)
    )

    hl3_results.append(
        compute_cluster_metrics(
            predicted=findSubCircuitHL3(data.netlist), ground_truth=data.hl3_gt
        )
    )

    return hl1_results, hl2_results, hl3_results
