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
# Step 1 & 2: Parse and classify MOSFETs
# -----------------------------------------------------------------------------
def parse_mosfets(netlist_text):
    mosfets = []
    for line in netlist_text.splitlines():
        line = line.strip()
        if not line or line.startswith("*") or not re.match(r"^[mM]", line):
            continue

        tokens = re.split(r"\s+", line)
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
# Step 3 & 4: Standard complementary inverter detection
# -----------------------------------------------------------------------------
def find_static_inverters(mosfets):
    vdd_names = {"vdd", "VDD", "Vdd", "supply"}
    gnd_names = {"gnd", "GND", "ground", "0"}

    # bucket by (gate, drain)
    bucket = defaultdict(lambda: {"PMOS": [], "NMOS": []})
    for m in mosfets:
        bucket[(m.gate, m.drain)][m.type].append(m)

    inverters = []
    for (gate, drain), pair in bucket.items():
        for p in pair["PMOS"]:
            if p.source not in vdd_names:
                continue
            for n in pair["NMOS"]:
                if n.source not in gnd_names:
                    continue

                inverters.append(
                    Inverter(
                        input_node=gate, output_node=drain, transistors=[p.name, n.name]
                    )
                )
    return inverters


# -----------------------------------------------------------------------------
# New Step: Diode‑load inverter detection
# -----------------------------------------------------------------------------
def find_diode_load_inverters(mosfets):
    """
    Finds patterns of:
      1) a diode‑connected PMOS load (gate==drain, source=VDD)
      2) a series PMOS pass‑device (source at that diode node, drain=Out)
      3) an NMOS pull‑down (drain=Out, source=GND)
    """
    vdd_names = {"vdd", "VDD", "Vdd", "supply"}
    gnd_names = {"gnd", "GND", "ground", "0"}

    results = []
    # 1) find diode‑connected PMOS
    diode_pmoss = [
        m
        for m in mosfets
        if m.type == "PMOS" and m.source in vdd_names and m.drain == m.gate
    ]

    for d in diode_pmoss:
        L = d.drain
        # 2) find any PMOS passing from L to Out
        series_pmoss = [
            m for m in mosfets if m.type == "PMOS" and m.source == L and m.drain != L
        ]
        for p2 in series_pmoss:
            Out = p2.drain
            # 3) find NMOS pulling Out to GND
            pull_nmos = [
                n
                for n in mosfets
                if n.type == "NMOS" and n.drain == Out and n.source in gnd_names
            ]
            for n in pull_nmos:
                # group them, we take p2 as logic pmos, d as load, n as pull-down
                # we treat the "input" as the NMOS gate here (n.gate)
                results.append(
                    Inverter(
                        input_node=n.gate,
                        output_node=Out,
                        transistors=[p2.name, d.name, n.name],
                    )
                )
    return results


# -----------------------------------------------------------------------------
# Step 5: (Optional) Pull in any helper devices on the same IN/OUT node
# -----------------------------------------------------------------------------
def extend_with_helpers(inverters, mosfets):
    by_gate = defaultdict(list)
    by_drain = defaultdict(list)
    for m in mosfets:
        by_gate[m.gate].append(m)
        by_drain[m.drain].append(m)

    extended = []
    for inv in inverters:
        nts = set(inv.transistors)
        # any other device on same gate?
        for m in by_gate[inv.input]:
            nts.add(m.name)
        # any other device on same drain?
        for m in by_drain[inv.output]:
            nts.add(m.name)

        extended.append(Inverter(inv.input, inv.output, sorted(nts)))
    return extended


# -----------------------------------------------------------------------------
# Step 6: Sanity‑check inverter action
# -----------------------------------------------------------------------------
def validate_inverter_logic(inverters, mosfets):
    valid = []
    for inv in inverters:
        fam = [m for m in mosfets if m.name in inv.transistors]
        has_p = any(m.type == "PMOS" and m.drain == inv.output for m in fam)
        has_n = any(m.type == "NMOS" and m.drain == inv.output for m in fam)
        if has_p and has_n:
            valid.append(inv)
    return valid


# -----------------------------------------------------------------------------
# Step 7: (Optional) Identify chains of inverters
# -----------------------------------------------------------------------------
def identify_chains(inverters):
    chains = []
    for i1 in inverters:
        for i2 in inverters:
            if i1.output == i2.input:
                chains.append((i1, i2))
    return chains


# -----------------------------------------------------------------------------
# Main API
# -----------------------------------------------------------------------------
def extract_inverters_from_netlist(netlist_text):
    mosfets = parse_mosfets(netlist_text)

    # both static complementary and diode‑load styles
    invs = []
    invs += find_static_inverters(mosfets)
    invs += find_diode_load_inverters(mosfets)

    # optionally include “helpers”
    invs = extend_with_helpers(invs, mosfets)

    # sanity‑check
    invs = validate_inverter_logic(invs, mosfets)

    # (you could identify chains here if you want)
    # chains = identify_chains(invs)

    # return as list of dicts
    # de‑dup by the sorted transistor list
    seen = set()
    out = []
    for inv in invs:
        key = tuple(inv.transistors)
        if key not in seen:
            seen.add(key)
            out.append(inv.to_dict())
    return out


# -----------------------------------------------------------------------------
# If run as a script, test your sample netlist:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    test_netlist = """\
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
    invs = extract_inverters_from_netlist(test_netlist)
    print(invs)
    # => [{'sub_circuit_name': 'Inverter', 'transistor_names': ['m15', 'm16', 'm14']}]
