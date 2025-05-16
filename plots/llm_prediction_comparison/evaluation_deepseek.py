from src.netlist import SPICENetlist
import glob
import json
from calc1 import compute_cluster_metrics, average_metrics
from typing import List, Any

from typing import List, Tuple, Dict, Set


import re
from collections import defaultdict, deque


from collections import defaultdict, Counter
from typing import List
import re
import itertools
from typing import List


def findSubCircuitHL1(netlist: str):
    """
    Find all diode-connected transistors and load/compensation capacitors subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """
    lines = [line.strip() for line in netlist.split("\n") if line.strip()]
    diode_connected = []
    load_caps = []
    comp_caps = []
    reference_nodes = {"ground", "gnd", "0", "vdd", "supply"}

    for line in lines:
        parts = line.split()
        if not parts:
            continue
        component = parts[0].lower()
        if component.startswith("m"):
            # Check for diode-connected MOSFET
            if len(parts) >= 3:
                drain = parts[1]
                gate = parts[2]
                if drain == gate:
                    diode_connected.append(parts[0])  # Preserve original case
        elif component.startswith("c"):
            # Classify as load or compensation capacitor
            if len(parts) >= 3:
                node1 = parts[1]
                node2 = parts[2]
                if node1 in reference_nodes or node2 in reference_nodes:
                    load_caps.append(parts[0])
                else:
                    comp_caps.append(parts[0])

    return [
        ["MosfetDiode", diode_connected],
        ["load_cap", load_caps],
        ["compensation_cap", comp_caps],
    ]


def findSubCircuitCM(netlist: str):
    """
    Find all Current Mirrors subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """
    from collections import defaultdict

    lines = [line.strip().split() for line in netlist.split("\n") if line.strip()]
    mosfets = []
    for parts in lines:
        if not parts:
            continue
        comp_type = parts[0].lower()
        if comp_type.startswith("m"):
            if len(parts) < 6:
                continue  # Invalid MOSFET line
            name = parts[0].lower()
            d_node = parts[1]
            g_node = parts[2]
            s_node = parts[3]
            b_node = parts[4]
            m_type = parts[5].lower()
            diode_connected = g_node == d_node
            mosfets.append(
                {
                    "name": name,
                    "type": m_type,
                    "d": d_node,
                    "g": g_node,
                    "s": s_node,
                    "b": b_node,
                    "diode": diode_connected,
                }
            )

    # Group by type and gate node
    groups = defaultdict(list)
    for mos in mosfets:
        key = (mos["type"], mos["g"])
        groups[key].append(mos)

    valid_groups = []
    for key in list(groups.keys()):
        subgroup = groups[key]
        m_type, gate_node = key

        # Step 3: Check for reference branch (diode or internal source connectivity)
        has_diode = any(m["diode"] for m in subgroup)
        if not has_diode:
            parent_ref = {}

            def find_ref(u):
                while parent_ref.get(u, u) != u:
                    parent_ref[u] = parent_ref.get(parent_ref[u], parent_ref[u])
                    u = parent_ref[u]
                return u

            def union_ref(u, v):
                pu = find_ref(u)
                pv = find_ref(v)
                if pu != pv:
                    parent_ref[pu] = pv

            nodes = set()
            for m in subgroup:
                nodes.add(m["d"])
                nodes.add(m["s"])
            for node in nodes:
                parent_ref[node] = node
            for m in subgroup:
                union_ref(m["d"], m["s"])
            s_nodes = [m["s"] for m in subgroup]
            if not s_nodes:
                continue
            root_ref = find_ref(s_nodes[0])
            all_connected = all(find_ref(s) == root_ref for s in s_nodes)
            if not all_connected:
                continue
            # Check bulk connection
            valid_b = all(m["b"] == m["s"] for m in subgroup)
            if not valid_b:
                continue

        # Step 4: Validate source consistency (common ground/supply)
        parent_source = {}

        def find_source(u):
            while parent_source.get(u, u) != u:
                parent_source[u] = parent_source.get(parent_source[u], parent_source[u])
                u = parent_source[u]
            return u

        def union_source(u, v):
            pu = find_source(u)
            pv = find_source(v)
            if pu != pv:
                parent_source[pu] = pv

        nodes_source = set()
        for m in subgroup:
            nodes_source.add(m["d"])
            nodes_source.add(m["s"])
        for node in nodes_source:
            parent_source[node] = node
        for m in subgroup:
            union_source(m["d"], m["s"])

        source_nodes = [m["s"] for m in subgroup]
        if not source_nodes:
            continue
        root_source = find_source(source_nodes[0])
        all_sources_connected = all(find_source(s) == root_source for s in source_nodes)
        if not all_sources_connected:
            continue

        # Check if the common source node is ground (NMOS) or supply (PMOS)
        if m_type == "nmos" and root_source.lower() != "ground":
            continue
        elif m_type == "pmos" and root_source.lower() != "supply":
            continue

        # Validate bulk connections
        valid_b = all(m["b"] == m["s"] for m in subgroup)
        if not valid_b:
            continue

        # Step 5: Check non-diode drain uniqueness
        non_diode = [m for m in subgroup if not m["diode"]]
        drains = [m["d"] for m in non_diode]
        if len(drains) != len(set(drains)):
            continue

        valid_groups.append(subgroup)

    # Step 6: Merge cascode structures
    type_groups = defaultdict(list)
    for group in valid_groups:
        m_type = group[0]["type"]
        type_groups[m_type].append(group)

    merged = []
    for m_type in type_groups:
        current_groups = type_groups[m_type]
        drain_map = defaultdict(list)
        # Build drain map using all drains
        for idx, group in enumerate(current_groups):
            for m in group:
                drain_map[m["d"]].append(idx)
        # Build edges between groups
        group_edges = defaultdict(list)
        for idx, group in enumerate(current_groups):
            gate = group[0]["g"]
            if gate in drain_map:
                group_edges[idx].extend(drain_map[gate])
        # Find connected components
        visited = set()
        components = []
        for idx in range(len(current_groups)):
            if idx not in visited:
                stack = [idx]
                component = []
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        component.append(node)
                        stack.extend(group_edges[node])
                components.append(component)
        # Merge groups in each component
        for comp in components:
            merged_group = []
            for group_idx in comp:
                merged_group.extend(current_groups[group_idx])
            # Remove duplicates
            seen = set()
            unique_mos = []
            for m in merged_group:
                if m["name"] not in seen:
                    seen.add(m["name"])
                    unique_mos.append(m)
            merged.append(unique_mos)
    valid_groups = merged

    # Step 7: Filter and finalize
    valid_groups = [g for g in valid_groups if len(g) >= 2]
    # Remove duplicates
    seen = set()
    unique = []
    for group in valid_groups:
        names = tuple(sorted([m["name"] for m in group], key=lambda x: int(x[1:])))
        if names not in seen:
            seen.add(names)
            unique.append(group)
    # Format output
    output = []
    for group in unique:
        names = sorted([m["name"] for m in group], key=lambda x: int(x[1:]))
        output.append(["CM", names])
    return output


def findSubCircuitDiffPair(netlist: str):
    """
    Find all Differential Pairs subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """
    from collections import defaultdict

    # Step 1: Extract MOSFET data
    mosfets = []
    for line in netlist.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts or not parts[0].startswith("M"):
            continue
        name = parts[0]
        d = parts[1]
        g = parts[2]
        s = parts[3]
        b = parts[4] if len(parts) > 4 else ""
        model = parts[5].lower() if len(parts) > 5 else ""
        mosfets.append({"name": name, "D": d, "G": g, "S": s, "B": b, "type": model})

    # Step 2: Group by type and B
    groups = defaultdict(list)
    for m in mosfets:
        key = (m["type"], m["B"])
        groups[key].append(m)

    differential_pairs = []

    # Process each group
    for group_key, group_mosfets in groups.items():
        typ, bulk = group_key

        # Step 3: Find candidate pairs
        candidates = []
        n = len(group_mosfets)
        for i in range(n):
            m1 = group_mosfets[i]
            for j in range(i + 1, n):
                m2 = group_mosfets[j]
                if m1["S"] == m2["S"] and m1["G"] != m2["G"] and m1["D"] != m2["D"]:
                    candidates.append((m1, m2))

        # Validate pairs and check load symmetry
        for m1, m2 in candidates:
            d1 = m1["D"]
            d2 = m2["D"]

            # Collect components connected to d1 and d2
            connected_d1 = []
            connected_d2 = []
            for m in mosfets:
                if m["name"] in (m1["name"], m2["name"]):
                    continue
                if d1 in (m["D"], m["G"], m["S"], m["B"]):
                    connected_d1.append(m)
                if d2 in (m["D"], m["G"], m["S"], m["B"]):
                    connected_d2.append(m)

            # Find symmetric loads
            symmetric_loads = []
            added = set()
            for cm1 in connected_d1:
                for cm2 in connected_d2:
                    if (
                        cm1["type"] == cm2["type"]
                        and cm1["name"] != cm2["name"]
                        and (
                            cm1["G"] == cm2["G"]
                            or (cm1["G"] == d2 and cm2["G"] == d1)
                            or (cm1["G"] == d1 and cm2["G"] == d2)
                        )
                    ):
                        if cm1["name"] not in added and cm2["name"] not in added:
                            symmetric_loads.extend([cm1["name"], cm2["name"]])
                            added.add(cm1["name"])
                            added.add(cm2["name"])

            # Form the differential pair group
            pair_names = [m1["name"], m2["name"]]
            all_components = pair_names + symmetric_loads
            sorted_components = sorted(all_components, key=lambda x: int(x[1:]))
            differential_pairs.append(("DiffPair", sorted_components))

    # Remove duplicate entries and convert tuples to lists
    unique = {}
    for dp in differential_pairs:
        key = (dp[0], tuple(dp[1]))
        if key not in unique:
            unique[key] = [dp[0], dp[1]]

    result = list(unique.values())
    return result


def findSubCircuitInverter(netlist: str):
    """
    Find all Inverters subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """
    lines = [line.strip().split() for line in netlist.split("\n") if line.strip()]

    # Extract MOSFETs
    mosfets = []
    for parts in lines:
        if parts[0].startswith("m"):
            mos_id = parts[0]
            drain = parts[1]
            gate = parts[2]
            source = parts[3]
            bulk = parts[4]
            mos_type = parts[5].lower()
            mosfets.append(
                {
                    "id": mos_id,
                    "D": drain,
                    "G": gate,
                    "S": source,
                    "B": bulk,
                    "type": mos_type,
                }
            )

    # Group by drain node (potential output nodes)
    drain_groups = {}
    for mos in mosfets:
        d = mos["D"]
        if d not in drain_groups:
            drain_groups[d] = []
        drain_groups[d].append(mos)

    # Build PMOS drain-to-source and NMOS drain-to-source mappings
    pmos_drain_map = {}
    nmos_drain_map = {}
    for mos in mosfets:
        if mos["type"] == "pmos":
            key = mos["D"]
            if key not in pmos_drain_map:
                pmos_drain_map[key] = []
            pmos_drain_map[key].append(mos)
        else:
            key = mos["D"]
            if key not in nmos_drain_map:
                nmos_drain_map[key] = []
            nmos_drain_map[key].append(mos)

    # Helper function to trace PMOS path to supply
    def trace_pmos_path(current_source, visited):
        if current_source == "supply":
            return []
        if current_source in visited:
            return None
        visited.add(current_source)
        # Look for PMOS transistors whose drain is the current source
        if current_source in pmos_drain_map:
            for pmos in pmos_drain_map[current_source]:
                next_source = pmos["S"]
                path = trace_pmos_path(next_source, visited.copy())
                if path is not None:
                    return [pmos] + path
        return None

    # Helper function to trace NMOS path to ground
    def trace_nmos_path(current_source, visited):
        if current_source == "ground":
            return []
        if current_source in visited:
            return None
        visited.add(current_source)
        # Look for NMOS transistors whose drain is the current source
        if current_source in nmos_drain_map:
            for nmos in nmos_drain_map[current_source]:
                next_source = nmos["S"]
                path = trace_nmos_path(next_source, visited.copy())
                if path is not None:
                    return [nmos] + path
        return None

    inverters = []

    for output_node, transistors in drain_groups.items():
        pmos_list = [m for m in transistors if m["type"] == "pmos"]
        nmos_list = [m for m in transistors if m["type"] == "nmos"]

        # Check all possible PMOS and NMOS pairs
        for pmos in pmos_list:
            pmos_path = trace_pmos_path(pmos["S"], set())
            if pmos_path is None:
                continue
            full_pmos = [pmos] + pmos_path

            for nmos in nmos_list:
                nmos_path = trace_nmos_path(nmos["S"], set())
                if nmos_path is None:
                    continue
                full_nmos = [nmos] + nmos_path

                # Collect unique transistor IDs
                all_ids = list({m["id"] for m in full_pmos + full_nmos})
                all_ids.sort(key=lambda x: int(x[1:]))
                inverters.append(["Inverter", all_ids])

    # Deduplicate inverters
    seen = set()
    unique = []
    for inv in inverters:
        key = tuple(inv[1])
        if key not in seen:
            seen.add(key)
            unique.append(inv)

    return unique


def findSubCircuitHL3(netlist: str):
    """
    Find all amplification stages, feedback stages, load and bias parts subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of tuples containing identified subcircuit names and the corresponding transistors.
    """
    lines = [line.strip().split() for line in netlist.split("\n") if line.strip()]
    transistors = []
    for parts in lines:
        if parts[0].startswith("m"):
            name = parts[0]
            drain = parts[1]
            gate = parts[2]
            source = parts[3]
            model = parts[5]
            transistors.append(
                {
                    "name": name,
                    "drain": drain,
                    "gate": gate,
                    "source": source,
                    "model": model,
                }
            )

    power_nodes = {"supply", "ground", "vdd", "gnd"}

    # Identify input nodes (explicit 'in' prefix)
    input_nodes = set()
    for t in transistors:
        gate = t["gate"].lower()
        if gate.startswith("in"):
            input_nodes.add(t["gate"])

    # Identify bias components: diode-connected and current mirrors
    diode_connected = {t["name"] for t in transistors if t["gate"] == t["drain"]}

    # Group transistors by (gate, model) for current mirrors
    gate_model_groups = {}
    for t in transistors:
        key = (t["gate"], t["model"])
        if key not in gate_model_groups:
            gate_model_groups[key] = []
        gate_model_groups[key].append(t["name"])
    current_mirrors = set()
    for group in gate_model_groups.values():
        if len(group) >= 2:
            current_mirrors.update(group)

    # Combine all bias candidates
    bias_part = list(diode_connected.union(current_mirrors))
    bias_set = set(bias_part)

    # Filter out bias transistors from stage consideration
    stage_transistors = [t for t in transistors if t["name"] not in bias_set]

    # First Stage: non-bias with gates in input_nodes
    first_stage = [t["name"] for t in stage_transistors if t["gate"] in input_nodes]
    first_drains = {t["drain"] for t in stage_transistors if t["name"] in first_stage}

    # Trace next_nodes from first_drains (non-bias transistors)
    next_nodes = set()
    for t in stage_transistors:
        if t["drain"] in first_drains:
            next_nodes.add(t["source"])
        if t["source"] in first_drains:
            next_nodes.add(t["drain"])

    # Second Stage: non-bias with gates in next_nodes
    second_stage = [t["name"] for t in stage_transistors if t["gate"] in next_nodes]
    second_drains = {t["drain"] for t in stage_transistors if t["name"] in second_stage}

    # Third Stage: non-bias with drain connected to output
    third_stage = [t["name"] for t in stage_transistors if t["drain"] == "out"]
    third_drains = {t["drain"] for t in stage_transistors if t["name"] in third_stage}

    # Combine second and third stages
    second_combined = list(set(second_stage + third_stage))

    # Load identification: connected to stage drains but not in stages or bias
    stage_drains = first_drains.union(second_drains, third_drains)
    load_candidates = []
    for t in transistors:
        if t["name"] in bias_set or t["name"] in (first_stage + second_combined):
            continue
        if (t["drain"] in stage_drains) or (t["source"] in stage_drains):
            load_candidates.append(t["name"])
    load_part = list(set(load_candidates))

    # Prepare result in required order
    result = []
    if first_stage:
        result.append(["firstStage", sorted(first_stage)])
    if second_combined:
        result.append(["secondStage", sorted(second_combined)])
    result.append(["loadPart", sorted(load_part)])
    result.append(["biasPart", sorted(bias_part)])

    # Ensure order matches test case
    ordered_result = []
    for key in ["firstStage", "secondStage", "loadPart", "biasPart"]:
        for item in result:
            if item[0] == key:
                ordered_result.append(item)
                break

    return ordered_result


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

    return findSubCircuitHL1(data.netlist), hl2_prediction, findSubCircuitHL3(data.netlist)

# hl1_info, hl2_info, hl3_info = code_eval()
# print("HL1 Evaluation")
# print("==" * 20)
# print(json.dumps(hl1_info, indent=2))

# print("HL2 Evaluation")
# print("==" * 20)
# print(json.dumps(hl2_info, indent=2))

# print("HL3 Evaluation")
# print("==" * 20)
# print(json.dumps(hl3_info, indent=2))
