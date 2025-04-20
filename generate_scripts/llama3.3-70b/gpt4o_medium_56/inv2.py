import re
import json
from collections import defaultdict


class Mosfet:
    """
    Represents a MOSFET instance in the netlist.
    Attributes:
        name (str): Instance name, e.g., m1
        type (str): 'pmos' or 'nmos'
        drain (str): Drain node
        gate (str): Gate node
        source (str): Source node
        bulk (str): Bulk/body node
    """

    def __init__(self, name, drain, gate, source, bulk, model):
        self.name = name
        self.drain = drain
        self.gate = gate
        self.source = source
        self.bulk = bulk
        m = model.lower()
        if "pmos" in m:
            self.type = "pmos"
        elif "nmos" in m:
            self.type = "nmos"
        else:
            raise ValueError(f"Unknown MOSFET type in model: {model}")

    def __repr__(self):
        return f"Mosfet({self.name}, {self.type}, D={self.drain}, G={self.gate}, S={self.source})"


def parse_netlist(filepath):
    """
    Step 1: Identify MOSFETs in the Netlist
    Parse the SPICE netlist file, returning a list of Mosfet objects.
    """
    mosfets = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            # Skip comments, capacitors, empty lines
            if not line or line.startswith("*") or re.match(r"^[cC]", line):
                continue
            parts = line.split()
            # MOSFET lines start with 'm' and end with 'nmos' or 'pmos'
            if re.match(r"^[mM]\w*", parts[0]) and parts[-1].lower() in (
                "nmos",
                "pmos",
            ):
                name = parts[0]
                # Expect: name drain gate source bulk model
                if len(parts) < 6:
                    raise ValueError(f"Invalid MOSFET line: {line}")
                drain, gate, source, bulk, model = (
                    parts[1],
                    parts[2],
                    parts[3],
                    parts[4],
                    parts[5],
                )
                mosfets.append(Mosfet(name, drain, gate, source, bulk, model))
    return mosfets


def find_basic_inverters(mosfets, vdd="supply", gnd="ground"):
    """
    Steps 2-4: Determine MOSFET types/connections, find complementary pairs, verify basic inverter.
    Returns list of dicts with keys: input, output, pmos, nmos.
    """
    # Group by gate node
    gate_groups = defaultdict(list)
    for m in mosfets:
        gate_groups[m.gate].append(m)

    inverters = []
    for gate, group in gate_groups.items():
        # PMOS pull-up devices with gate, source=VDD
        pmos_devices = [m for m in group if m.type == "pmos" and m.source == vdd]
        # NMOS pull-down devices with gate, source=GND
        nmos_devices = [m for m in group if m.type == "nmos" and m.source == gnd]
        for p in pmos_devices:
            for n in nmos_devices:
                # Check drains tied together for output
                if p.drain == n.drain:
                    out_node = p.drain
                    # Ensure no other connection prevents inverter (simple check)
                    connected_drains = [m for m in mosfets if m.drain == out_node]
                    # Exactly two devices on drain
                    if len(connected_drains) == 2:
                        inverters.append(
                            {"input": gate, "output": out_node, "pmos": p, "nmos": n}
                        )
    return inverters


def include_additional_transistors(inverters, mosfets):
    """
    Step 5: Include additional transistors connected to input or output nodes
    that do not disrupt basic inverter function.
    Returns list of inverter dicts with full transistor lists.
    """
    enhanced = []
    for inv in inverters:
        input_node = inv["input"]
        output_node = inv["output"]
        core = {inv["pmos"].name, inv["nmos"].name}
        # Find devices tied to output (drain or gate) or input (drain or gate)
        extras = []
        for m in mosfets:
            if m.name in core:
                continue
            # connected to input or output nodes
            if (
                m.drain == output_node
                or m.gate == output_node
                or m.source == output_node
            ):
                extras.append(m.name)
            elif (
                m.drain == input_node or m.gate == input_node or m.source == input_node
            ):
                extras.append(m.name)
        # Append extras but ensure they don't break two-device drain
        transistors = sorted(core.union(extras))
        enhanced.append(
            {"sub_circuit_name": "Inverter", "transistor_names": transistors}
        )
    return enhanced


def find_inverter_chains(inverters):
    """
    Step 7: Identify chains where output of one inverter is input to another.
    Returns list of chains, each as list of transistor name groups.
    """
    # Map input->inverter and output->inverter indices
    input_map = {inv["input"]: idx for idx, inv in enumerate(inverters)}
    output_map = {inv["output"]: idx for idx, inv in enumerate(inverters)}
    chains = []
    visited = set()
    for idx, inv in enumerate(inverters):
        if idx in visited:
            continue
        chain = [idx]
        visited.add(idx)
        # follow outputs
        cur_out = inv["output"]
        while cur_out in input_map:
            next_idx = input_map[cur_out]
            if next_idx in visited:
                break
            chain.append(next_idx)
            visited.add(next_idx)
            cur_out = inverters[next_idx]["output"]
        chains.append(chain)
    return chains


def main(netlist_path, vdd="supply", gnd="ground"):
    mosfets = parse_netlist(netlist_path)
    basic = find_basic_inverters(mosfets, vdd, gnd)
    detailed = include_additional_transistors(basic, mosfets)
    chains_idx = find_inverter_chains(detailed)

    # Format output
    output = detailed
    # Optionally, could add chain info
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Identify inverters in a SPICE netlist"
    )
    parser.add_argument("netlist", help="Path to SPICE netlist file")
    parser.add_argument("--vdd", default="supply", help="VDD node name")
    parser.add_argument("--gnd", default="ground", help="GND node name")
    args = parser.parse_args()
    main(args.netlist, args.vdd, args.gnd)
