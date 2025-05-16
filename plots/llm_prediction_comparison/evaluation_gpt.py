from src.netlist import SPICENetlist
import glob
import json
from calc1 import compute_cluster_metrics, average_metrics
from examples.measure_fn2 import (
    evaluate_graph_clustering_node_wise,
    evaluate_graph_clustering_class_wise,
    create_confusion_matrix,
    aggregate_confusion_matrices,
)
from typing import List, Any

from typing import List, Tuple, Dict, Set


import re
from collections import defaultdict, deque


from collections import defaultdict, Counter
from typing import List
import re
import itertools
from typing import List


def findSubCircuitDiffPair(netlist: str) -> List[List]:
    """
    Find all Differential Pairs subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component
                       and its connections in the circuit.

    Returns:
        List of [subcircuit_name, [transistor names...]].
    """
    # 1. Parse MOSFET lines
    devices = []
    for line in netlist.splitlines():
        tokens = line.strip().split()
        if not tokens:
            continue
        # MOSFET lines start with 'm' or 'M' and have at least 6 tokens
        if tokens[0][0].lower() == "m" and len(tokens) >= 6:
            name = tokens[0]
            drain, gate, source, bulk = tokens[1], tokens[2], tokens[3], tokens[4]
            devtype = tokens[5].lower()
            if devtype in ("nmos", "pmos"):
                devices.append(
                    {
                        "name": name,
                        "type": devtype,
                        "drain": drain,
                        "gate": gate,
                        "source": source,
                        "bulk": bulk,
                    }
                )

    # 2. Group by device type
    groups = {
        "nmos": [d for d in devices if d["type"] == "nmos"],
        "pmos": [d for d in devices if d["type"] == "pmos"],
    }

    found = []

    # For each type (we'll pick up NMOS pairs here, but code checks both)
    for devtype, trans_list in groups.items():
        # 3. all unique pairs
        for t1, t2 in itertools.combinations(trans_list, 2):
            # 4. shared source
            if t1["source"] != t2["source"]:
                continue
            # 5. distinct gate & drain
            if t1["gate"] == t2["gate"] or t1["drain"] == t2["drain"]:
                continue
            # 6. same bulk
            if t1["bulk"] != t2["bulk"]:
                continue
            # 7. same type already ensured, drains not tied, sources tied
            # 8. simple differential‐input naming: both gates start with 'in'
            g1, g2 = t1["gate"], t2["gate"]
            if not (g1.startswith("in") and g2.startswith("in")):
                continue

            # 11. find the two "load" (cascode) devices:
            #     one whose source == t1.drain, and one whose source == t2.drain,
            #     and which share a common gate
            loads1 = [d for d in devices if d["source"] == t1["drain"]]
            loads2 = [d for d in devices if d["source"] == t2["drain"]]
            if len(loads1) != 1 or len(loads2) != 1:
                continue
            l1, l2 = loads1[0], loads2[0]
            if l1["gate"] != l2["gate"]:
                continue

            # Record the four‐device differential pair (inputs + cascodes)
            names = [t1["name"], t2["name"], l1["name"], l2["name"]]
            found.append(["DiffPair", names])

    return found


def findSubCircuitCM(netlist: str):
    """
    Find all Current Mirrors subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of lists, each containing the subcircuit name 'CM' and the list of transistor instance names that form a current mirror.
    """
    # 1. Parse MOSFETs
    lines = [
        l.strip()
        for l in netlist.splitlines()
        if l.strip() and not l.strip().startswith("*")
    ]
    mosfets = []
    for line in lines:
        if line[0].lower() == "m":
            toks = line.split()
            name = toks[0]
            d, g, s, b = toks[1], toks[2], toks[3], toks[4]
            model = toks[5].lower()
            if "nmos" in model:
                mtype = "nmos"
            elif "pmos" in model:
                mtype = "pmos"
            else:
                mtype = model
            mosfets.append(
                {
                    "name": name,
                    "drain": d,
                    "gate": g,
                    "source": s,
                    "bulk": b,
                    "type": mtype,
                }
            )

    # 2. Group by type
    mos_by_type = {"nmos": [], "pmos": []}
    for m in mosfets:
        if m["type"] in mos_by_type:
            mos_by_type[m["type"]].append(m)

    simple_mirrors = []
    cascoded_mirrors = []
    suppressed_gates = set()

    # 3. Cascoded detection
    for mtype, devs in mos_by_type.items():
        gate_groups = {}
        for m in devs:
            gate_groups.setdefault(m["gate"], []).append(m)

        for gate_net, casg in gate_groups.items():
            if len(casg) < 2:
                continue
            # all share source & bulk
            if (
                len({m["source"] for m in casg}) != 1
                or len({m["bulk"] for m in casg}) != 1
            ):
                continue

            # map each cascode device -> a main whose source == cas.drain
            mapping = {}
            for cas in casg:
                for main in devs:
                    if main not in casg and main["source"] == cas["drain"]:
                        mapping[cas["name"]] = main
                        break

            if len(mapping) != len(casg):
                continue

            mains = list(mapping.values())
            if len({m["gate"] for m in mains}) != 1 or len(mains) < 2:
                continue

            # success: cascoded mirror
            names = sorted([m["name"] for m in casg + mains])  # order no longer matters
            cascoded_mirrors.append(["CM", names])

            # suppress both cascode‐gate and primary‐gate
            suppressed_gates.add(gate_net)
            suppressed_gates.add(next(iter(m["gate"] for m in mains)))

    # 4. Simple mirror detection on the remaining gates
    for mtype, devs in mos_by_type.items():
        gate_groups = {}
        for m in devs:
            gate_groups.setdefault(m["gate"], []).append(m)

        for gate_net, group in gate_groups.items():
            if gate_net in suppressed_gates or len(group) < 2:
                continue
            if (
                len({m["source"] for m in group}) == 1
                and len({m["bulk"] for m in group}) == 1
                and any(m["drain"] == m["gate"] for m in group)
            ):
                names = sorted([m["name"] for m in group])
                simple_mirrors.append(["CM", names])

    # 5. Combine, dedupe
    all_mirrors = cascoded_mirrors + simple_mirrors
    unique = []
    seen = set()
    for tag, names in all_mirrors:
        key = frozenset(names)
        if key not in seen:
            seen.add(key)
            unique.append([tag, names])

    # (outer‐list order doesn’t matter per spec)
    return unique


def findSubCircuitInverter(netlist: str) -> List[List]:
    """
    Find all Inverter subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

    Returns:
        List of [subcircuit name, list of transistor instance names].
    """
    # 1. Parse MOSFETs
    devices = []
    for line in netlist.splitlines():
        line = line.strip()
        if not line or line.startswith("*"):
            continue
        parts = line.split()
        if parts[0][0].lower() == "m" and len(parts) >= 6:
            name = parts[0]
            d, g, s, b = parts[1], parts[2], parts[3], parts[4]
            dev_type = parts[5].lower()
            devices.append(
                {
                    "name": name,
                    "type": dev_type,
                    "drain": d,
                    "gate": g,
                    "source": s,
                    "bulk": b,
                }
            )
    assert devices, "❌ No MOSFETs found."

    # 2. Identify ground & supply
    ground_cands = {"0", "gnd", "ground"}
    supply_cands = {"vdd", "vcc", "vss", "vsupply", "supply"}
    nmos_sb = [d["source"] for d in devices if d["type"] == "nmos"] + [
        d["bulk"] for d in devices if d["type"] == "nmos"
    ]
    pmos_sb = [d["source"] for d in devices if d["type"] == "pmos"] + [
        d["bulk"] for d in devices if d["type"] == "pmos"
    ]

    ground = next(
        (g for g in ground_cands if g in nmos_sb), Counter(nmos_sb).most_common(1)[0][0]
    )
    supply = next(
        (v for v in supply_cands if v in pmos_sb), Counter(pmos_sb).most_common(1)[0][0]
    )

    # 3. Candidate outputs: shared drains
    drains_n = {d["drain"] for d in devices if d["type"] == "nmos"}
    drains_p = {d["drain"] for d in devices if d["type"] == "pmos"}
    shared = drains_n & drains_p
    assert shared, "❌ No shared drains (no inverter outputs)."

    # 6. Filter simple outputs: never used as gate or source
    gates = {d["gate"] for d in devices}
    sources = {d["source"] for d in devices}
    simple_outs = {n for n in shared if n not in gates and n not in sources}

    # For Test Case 1 we expect exactly {'out'}
    # assert simple_outs == {
    #     "out"
    # }, f"❌ Unexpected simple-outputs: {simple_outs} (expected {{'out'}})"

    # helper: build series chains
    def build_chains(dev_type, out_net, end_net):
        by_d = defaultdict(list)
        for d in devices:
            if d["type"] == dev_type:
                by_d[d["drain"]].append(d)
        chains = []

        def dfs(curr, path):
            for dev in by_d.get(curr, []):
                nxt = dev["source"]
                if nxt == end_net:
                    chains.append(path + [dev])
                else:
                    dfs(nxt, path + [dev])

        dfs(out_net, [])
        return chains

    inverters = []
    for out in simple_outs:
        pu = build_chains("pmos", out, supply)
        pd = build_chains("nmos", out, ground)
        # Expect exactly one chain each
        # assert (
        #     len(pu) == 1
        # ), f"❌ PMOS chains for '{out}': {[[d['name'] for d in c] for c in pu]}"
        # assert (
        #     len(pd) == 1
        # ), f"❌ NMOS chains for '{out}': {[[d['name'] for d in c] for c in pd]}"

        names = [d["name"] for d in pu[0] + pd[0]]
        inverters.append(["Inverter", names])

    # Structural check: list of [str, list]
    for idx, entry in enumerate(inverters):
        # assert (
        #     isinstance(entry, list) and len(entry) == 2
        # ), f"❌ Entry #{idx} wrong type/length: {entry!r}"
        # assert isinstance(
        #     entry[0], str
        # ), f"❌ Entry #{idx} first element not a string: {entry[0]!r}"
        # assert isinstance(
        #     entry[1], list
        # ), f"❌ Entry #{idx} second element not a list: {entry[1]!r}"
        pass

    return inverters


def findSubCircuitHL1(netlist: str):
    """
    Find all diode-connected transistors and load/compensation capacitors subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string, where each line defines a component
                       and its connections in the circuit.

    Returns:
        List of lists: [
            ['MosfetDiode',    [<diode-connected transistor names>]],
            ['load_cap',       [<load capacitor names>]],
            ['compensation_cap',[<comp capacitor names>]]
        ]
    """
    # sets for classification (lower-case)
    output_nodes = {"out", "vout", "output"}
    ground_nodes = {"0", "gnd", "ground"}
    supply_nodes = {"vdd", "vss", "supply"}

    diode_transistors = []
    load_caps = []
    comp_caps = []

    for line in netlist.splitlines():
        line = line.strip()
        if not line or line.startswith("*") or line.startswith(";"):
            continue

        tokens = line.split()
        inst = tokens[0].lower()

        # Transistor lines start with 'm'
        if inst.startswith("m") and len(tokens) >= 6:
            name = tokens[0]
            drain = tokens[1].lower()
            gate = tokens[2].lower()
            # source = tokens[3]
            # bulk   = tokens[4]
            # dev_type = tokens[5].lower()  # nmos/pmos, not needed here
            if drain == gate:
                diode_transistors.append(name)

        # Capacitor lines start with 'c'
        elif inst.startswith("c") and len(tokens) >= 3:
            name = tokens[0]
            node1 = tokens[1].lower()
            node2 = tokens[2].lower()

            # Load capacitor: one end is output, the other is ground
            if (node1 in output_nodes and node2 in ground_nodes) or (
                node2 in output_nodes and node1 in ground_nodes
            ):
                load_caps.append(name)

            # Compensation capacitor: one end is output & the other is an internal node...
            # ...or both ends are internal nodes
            else:
                # check if node is “internal”
                def is_internal(n):
                    return (
                        n not in output_nodes
                        and n not in ground_nodes
                        and n not in supply_nodes
                    )

                if (
                    (node1 in output_nodes and is_internal(node2))
                    or (node2 in output_nodes and is_internal(node1))
                    or (is_internal(node1) and is_internal(node2))
                ):
                    comp_caps.append(name)

    return [
        ["MosfetDiode", diode_transistors],
        ["load_cap", load_caps],
        ["compensation_cap", comp_caps],
    ]


from collections import deque


def findSubCircuitHL3(netlist: str):
    """
    Find all amplification stages, feedback stage, load and bias parts subcircuits.

    Args:
        netlist (str): A flat SPICE netlist as a string.

    Returns:
        List of [category, [transistor names]], for non-empty categories.
    """
    # --- 1. Parse netlist ---
    lines = [l.strip() for l in netlist.splitlines()]
    transistors = []
    other_comps = []
    for line in lines:
        if not line or line.startswith("*"):
            continue
        parts = line.split()
        name = parts[0]
        if name.lower().startswith("m") and len(parts) >= 6:
            d, g, s, b, ttype = parts[1:6]
            transistors.append(
                {
                    "name": name,
                    "drain": d,
                    "gate": g,
                    "source": s,
                    "bulk": b,
                    "type": ttype.lower(),
                }
            )
        else:
            other_comps.append({"name": parts[0], "nodes": parts[1:]})

    # --- 2. Identify input/output nets ---
    input_nodes = {t["gate"] for t in transistors if t["gate"].lower().startswith("in")}
    output_nodes = {
        t["drain"] for t in transistors if t["drain"].lower().startswith("out")
    }

    # --- 3. First amplification stage (gate=input) ---
    firstStage = [t["name"] for t in transistors if t["gate"] in input_nodes]

    # --- 3b. Second stage = pull-down NMOS onto OUT ---
    secondStage = [
        t["name"]
        for t in transistors
        if t["type"] == "nmos"
        and t["drain"] in output_nodes
        and t["name"] not in firstStage
    ]

    # --- 6. Feedback stage (any comp tying an IN net back to OUT) ---
    feedbackStage = []
    for t in transistors:
        nets = {t["drain"], t["gate"], t["source"], t["bulk"]}
        if (nets & input_nodes) and (nets & output_nodes):
            feedbackStage.append(t["name"])
    for c in other_comps:
        nets = set(c["nodes"])
        if (nets & input_nodes) and (nets & output_nodes):
            feedbackStage.append(c["name"])
    feedbackStage = list(dict.fromkeys(feedbackStage))

    # --- prepare exclusion sets ---
    stage_and_fb = set(firstStage + secondStage + feedbackStage)

    # --- 4. Identify “bias candidates” to exclude from load BFS ---
    biasCandidates = set()
    for t in transistors:
        # diode‐connected
        if t["gate"] == t["drain"]:
            biasCandidates.add(t["name"])
        # supply/ground shorts
        if t["type"] == "pmos" and t["source"] == t["drain"] == "supply":
            biasCandidates.add(t["name"])
        if t["type"] == "nmos" and t["source"] == t["drain"] == "ground":
            biasCandidates.add(t["name"])
        # tied to ibias
        if t["gate"] == "ibias" or t["drain"] == "ibias":
            biasCandidates.add(t["name"])

    # --- 4. Load parts: BFS from firstStage drains, *only* over internal nets (no supply/ground) ---
    fs_drains = {t["drain"] for t in transistors if t["name"] in firstStage}
    queue = deque(fs_drains)
    discovered = set(fs_drains)
    loadPart = []
    excluded = stage_and_fb | biasCandidates

    while queue:
        net = queue.popleft()
        for t in transistors:
            if t["name"] in excluded or t["name"] in loadPart:
                continue
            # only traverse via drain↔source on *internal* nets
            if net == t["drain"] or net == t["source"]:
                loadPart.append(t["name"])
                # enqueue the *other* terminal, if it’s not supply/ground
                for nxt in (t["drain"], t["source"]):
                    if nxt not in discovered and nxt not in {"supply", "ground"}:
                        discovered.add(nxt)
                        queue.append(nxt)

    # --- 5 & 7. Bias parts = all remaining transistors ---
    assigned = stage_and_fb | set(loadPart)
    biasPart = [t["name"] for t in transistors if t["name"] not in assigned]

    # --- 8. Build result ---
    result = []
    if firstStage:
        result.append(["firstStage", firstStage])
    if secondStage:
        result.append(["secondStage", secondStage])
    if feedbackStage:
        result.append(["feedbackStage", feedbackStage])
    if loadPart:
        result.append(["loadPart", loadPart])
    if biasPart:
        result.append(["biasPart", biasPart])
    return result


def code_eval(subsets=["small", "medium", "large"]):
    hl1_info = {}
    hl2_info = {}
    hl3_info = {}

    cfm = {}

    for subset in subsets:
        hl1_results = []
        hl2_results = []
        hl3_results = []

        hl1_cf_matries = []
        hl2_cf_matries = []
        hl3_cf_matries = []

        for i in range(1, 101):
            data = SPICENetlist(f"data/asi-fuboco-test/{subset}/{i}/")

            hl1_prediction = findSubCircuitHL1(data.netlist)
            hl1_results.append(
                evaluate_graph_clustering_node_wise(
                    prediction=hl1_prediction, ground_truth=data.hl1_gt
                )
            )
            hl1_cf_matries.append(create_confusion_matrix(data.hl1_gt, hl1_prediction))

            cm = findSubCircuitCM(data.netlist)
            dp = findSubCircuitDiffPair(data.netlist)
            invs = findSubCircuitInverter(data.netlist)
            hl2_prediction = cm + dp + invs
            hl2_results.append(
                evaluate_graph_clustering_node_wise(
                    prediction=hl2_prediction, ground_truth=data.hl2_gt
                )
            )

            hl2_cf_matries.append(create_confusion_matrix(data.hl2_gt, hl2_prediction))

            hl3_prediction = findSubCircuitHL3(data.netlist)
            hl3_results.append(
                evaluate_graph_clustering_node_wise(
                    prediction=hl3_prediction, ground_truth=data.hl3_gt
                )
            )
            hl3_cf_matries.append(create_confusion_matrix(data.hl3_gt, hl3_prediction))

        hl1_info[subset] = average_metrics(hl1_results)
        hl2_info[subset] = average_metrics(hl2_results)
        hl3_info[subset] = average_metrics(hl3_results)
        cfm[subset] = {
            "HL1": aggregate_confusion_matrices(hl1_cf_matries),
            "HL2": aggregate_confusion_matrices(hl2_cf_matries),
            "HL3": aggregate_confusion_matrices(hl3_cf_matries),
        }
    return hl1_info, hl2_info, hl3_info, cfm


def aggregate_confusion_matrices_over_subsets(cfm):
    """
    Aggregates confusion matrices across subsets (e.g., small, medium, large).

    Args:
        cfm: Dictionary containing confusion matrices for each subset and hierarchical level.

    Returns:
        A dictionary with aggregated confusion matrices for each hierarchical level.
    """
    aggregated_cfm = {
        "HL1": defaultdict(lambda: defaultdict(int)),
        "HL2": defaultdict(lambda: defaultdict(int)),
        "HL3": defaultdict(lambda: defaultdict(int)),
    }

    for subset, levels in cfm.items():
        for level, matrix in levels.items():
            for gt_name, pred_dict in matrix.items():
                for pred_name, count in pred_dict.items():
                    aggregated_cfm[level][gt_name][pred_name] += count

    return aggregated_cfm


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

    return (
        findSubCircuitHL1(data.netlist),
        hl2_prediction,
        findSubCircuitHL3(data.netlist),
    )


# hl1_info, hl2_info, hl3_info, cfm = code_eval()
# aggregated_cfm = aggregate_confusion_matrices_over_subsets(cfm)

# print("HL1 Evaluation")
# print("==" * 20)
# print(json.dumps(hl1_info, indent=2))

# print("HL2 Evaluation")
# print("==" * 20)
# print(json.dumps(hl2_info, indent=2))

# print("HL3 Evaluation")
# print("==" * 20)
# print(json.dumps(hl3_info, indent=2))


# print("Confusion Matrix")
# print("==" * 20)
# for subset in cfm:
#     print(f"Subset: {subset}")
#     print("--" * 10)
#     for level in ["HL1", "HL2", "HL3"]:
#         for gt_name, pred_dict in cfm[subset][level].items():
#             print(f"{gt_name}:")
#             for pred_name, count in pred_dict.items():
#                 print(f"  {pred_name}: {count}")


# print("Aggregated Confusion Matrix")
# print("==" * 20)
# for level in ["HL1", "HL2", "HL3"]:
#     print(f"Level: {level}")
#     print("--" * 10)
#     for gt_name, pred_dict in aggregated_cfm[level].items():
#         print(f"{gt_name}:")
#         for pred_name, count in pred_dict.items():
#             print(f"  {pred_name}: {count}")
