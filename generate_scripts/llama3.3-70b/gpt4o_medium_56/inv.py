#!/usr/bin/env python3
import re
from collections import defaultdict, namedtuple

# -----------------------------------------------------------------------------
# Data structures
# -----------------------------------------------------------------------------
Mosfet = namedtuple("Mosfet", ["name", "drain", "gate", "source", "bulk", "type"])


class Inverter:
    def __init__(self, input_node, output_node, transistors):
        self.input = input_node
        self.output = output_node
        self.transistors = transistors  # list of Mosfet.name

    def to_dict(self):
        return {"sub_circuit_name": "Inverter", "transistor_names": self.transistors}


# -----------------------------------------------------------------------------
# Step 1: Parse and Identify MOSFETs
# -----------------------------------------------------------------------------
def parse_mosfets(netlist_text):
    """
    Return a list of Mosfet(name, drain, gate, source, bulk, type)
    for every line beginning with 'm' or containing 'nmos'/'pmos'.
    """
    mosfets = []
    for line in netlist_text.splitlines():
        line = line.strip()
        # skip comments and empty lines
        if not line or line.startswith("*"):
            continue

        # quick check for MOSFET lines
        if not re.match(r"^[mM]\w*", line):
            continue

        tokens = re.split(r"\s+", line)
        # need at least 6 tokens: name, drain, gate, source, bulk, type
        if len(tokens) < 6:
            continue

        name, drain, gate, source, bulk, mtype = tokens[:6]
        mtype_low = mtype.lower()
        if mtype_low not in ("pmos", "nmos"):
            continue

        mosfets.append(
            Mosfet(
                name=name,
                drain=drain,
                gate=gate,
                source=source,
                bulk=bulk,
                type=mtype_low.upper(),
            )
        )
    return mosfets


# -----------------------------------------------------------------------------
# Step 3 & 4: Find complementary pairs & verify inverter topology
# -----------------------------------------------------------------------------
def find_static_inverters(mosfets):
    vdd_names = set(["vdd", "VDD", "Vdd", "supply"])
    gnd_names = set(["gnd", "GND", "ground", "0"])

    # bucket by (gate, drain)
    bucket = defaultdict(lambda: {"PMOS": [], "NMOS": []})
    for m in mosfets:
        bucket[(m.gate, m.drain)][m.type].append(m)

    inverters = []
    for (gate, drain), pair in bucket.items():
        # need at least one PMOS and one NMOS
        for p in pair["PMOS"]:
            if p.source not in vdd_names:
                continue
            for n in pair["NMOS"]:
                if n.source not in gnd_names:
                    continue

                # we have a candidate inverter: p & n share gate & drain
                inverters.append(
                    Inverter(
                        input_node=gate, output_node=drain, transistors=[p.name, n.name]
                    )
                )

    return inverters


# -----------------------------------------------------------------------------
# Step 5: Pull in any “helper” devices that attach only to IN or OUT
# -----------------------------------------------------------------------------
def extend_with_helpers(inverters, mosfets):
    """
    For each inverter, look for any other mosfets whose gate==input or drain==output
    but that do not break the 2‑transistor static inverter shape, and attach them.
    """
    # index by gate and by drain
    by_gate = defaultdict(list)
    by_drain = defaultdict(list)
    for m in mosfets:
        by_gate[m.gate].append(m)
        by_drain[m.drain].append(m)

    extended = []
    for inv in inverters:
        nt = set(inv.transistors)
        # any other device on same gate?
        for m in by_gate[inv.input]:
            if m.name not in nt:
                nt.add(m.name)
        # any other device on same drain?
        for m in by_drain[inv.output]:
            if m.name not in nt:
                nt.add(m.name)

        # record extended inverter
        ext = Inverter(inv.input, inv.output, sorted(nt))
        extended.append(ext)
    return extended


# -----------------------------------------------------------------------------
# Step 6: (Basic) Validate that the pull‑up / pull‑down action is complementary
# -----------------------------------------------------------------------------
def validate_inverter_logic(inverters, mosfets):
    """
    Very simple check: ensure that for each inverter,
    one pmos and one nmos exist whose gates==input & drains==output.
    """
    ok = []
    for inv in inverters:
        fam = [m for m in mosfets if m.name in inv.transistors]
        has_p = any(
            m.type == "PMOS" and m.gate == inv.input and m.drain == inv.output
            for m in fam
        )
        has_n = any(
            m.type == "NMOS" and m.gate == inv.input and m.drain == inv.output
            for m in fam
        )
        if has_p and has_n:
            ok.append(inv)
    return ok


# -----------------------------------------------------------------------------
# Step 7: Identify chains of back‑to‑back inverters
# -----------------------------------------------------------------------------
def identify_chains(inverters):
    """
    Look for inv1.output == inv2.input
    and chain them.
    """
    chains = []
    # simple O(n^2) search
    for i1 in inverters:
        for i2 in inverters:
            if i1.output == i2.input:
                chains.append((i1, i2))
    return chains


# -----------------------------------------------------------------------------
# Main API
# -----------------------------------------------------------------------------
def extract_inverters_from_netlist(netlist_text):
    # Step 1 & 2
    mosfets = parse_mosfets(netlist_text)

    # Step 3 & 4
    static_invs = find_static_inverters(mosfets)

    # Step 5
    extended = extend_with_helpers(static_invs, mosfets)

    # Step 6
    validated = validate_inverter_logic(extended, mosfets)

    # Step 7 (optional, shown here but not returned)
    chains = identify_chains(validated)

    # Prepare output
    return [inv.to_dict() for inv in validated]


# -----------------------------------------------------------------------------
# Example usage on your test case
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    netlist = """
    c1 a out
    m1  b ibias ground ground nmos
    m2  c ibias ground ground nmos
    m3  d ibias ground ground nmos
    m4  e b supply supply pmos
    m5  f e g g nmos
    m6  a e h h nmos
    m7  f d i i pmos
    m8  i f supply supply pmos
    m9  a d j j pmos
    m10 j f supply supply pmos
    m11 k ibias ground ground nmos
    m12 g in1 k k nmos
    m13 h in2 k k nmos
    c2  out ground
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
    inv_list = extract_inverters_from_netlist(netlist)
    print(inv_list)
    # => should print something like:
    #   [{'sub_circuit_name': 'Inverter', 'transistor_names': ['m14','m15','m16']}, …]
