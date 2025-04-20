import glob
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from calc1 import compute_cluster_metrics, average_metrics
from src.netlist import SPICENetlist
from prompt_collections.rules import (
    create_gen_rule_prompt,
    create_update_rule_prompt,
    gen_instruction_prompt,
    update_instruction_prompt,
    update_instruction_prompt_v2,
)

from prompt_collections.hl2 import (
    create_prompt_hl2,
    create_prompt_hl2_multiple_subcircuits_with_rule_provided,
    create_prompt_hl2_multiple_subcircuits_with_rule_provided_v2,
)

from main import llm_invoke, identify_devices
from models import (
    load_ollama,
    load_openai,
    load_deepseek,
)

from utils import ppformat, configure_logging

# -----
from loguru import logger
import sys
import datetime


# -----


def check_add(list_subcircuits, counter):
    """Check if any of the subcircuits in could be used as demonstration circuits."""
    should_add = False
    for sc in list_subcircuits:
        if sc in counter and counter[sc] == 0:
            counter[sc] = 1
            should_add = True
    return should_add


def get_demonstration_examples(samples):
    all_examples = []
    available_subcircuit_names = list(
        {
            "MosfetAnalogInverter",
            "MosfetDiodeArray",
            "MosfetCascodedAnalogInverter",
            "MosfetCascodedNMOSAnalogInverter",
            "MosfetImprovedWilsonCurrentMirror",
            "MosfetDifferentialPair",
            "MosfetCascodeCurrentMirror",
            "CapacitorArray",
            "MosfetFourTransistorCurrentMirror",
            "MosfetWilsonCurrentMirror",
            "MosfetCascodeAnalogInverterNmosDiodeTransistor",
            "MosfetCascodedDifferentialPair",
            "MosfetWideSwingCascodeCurrentMirror",
            "MosfetSimpleCurrentMirror",
            "MosfetFoldedCascodeDifferentialPair",
            "MosfetCascodeAnalogInverterPmosDiodeTransistor",
            "MosfetNormalArray",
            "MosfetCascodeNMOSAnalogInverterOneDiodeTransistor",
            "MosfetCascodeAnalogInverterNmosCurrentMirrorLoad",
            "MosfetCascodedPMOSAnalogInverter",
            "MosfetCascodePMOSAnalogInverterOneDiodeTransistor",
        }
    )
    counter = {k: 0 for k in available_subcircuit_names}

    for dir in ["small", "medium"]:
        for i in samples:  # range(1, 101):
            netlist_dir = f"data/asi-fuboco-train/{dir}/{i}/"
            tree = ET.parse(
                glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0]
            )
            root = tree.getroot()
            subcircuits = root[1]

            all_subcircuits = []
            for sc in subcircuits:
                circuit_name = sc.attrib["name"]
                circuit_name = circuit_name[: circuit_name.find("[")]
                all_subcircuits.append(circuit_name)

            if check_add(all_subcircuits, counter):
                all_examples.append(netlist_dir)

    return all_examples


def check_cover(examples):
    available_subcircuit_names = list(
        {
            "MosfetAnalogInverter",
            "MosfetDiodeArray",
            "MosfetCascodedAnalogInverter",
            "MosfetCascodedNMOSAnalogInverter",
            "MosfetImprovedWilsonCurrentMirror",
            "MosfetDifferentialPair",
            "MosfetCascodeCurrentMirror",
            "CapacitorArray",
            "MosfetFourTransistorCurrentMirror",
            "MosfetWilsonCurrentMirror",
            "MosfetCascodeAnalogInverterNmosDiodeTransistor",
            "MosfetCascodedDifferentialPair",
            "MosfetWideSwingCascodeCurrentMirror",
            "MosfetSimpleCurrentMirror",
            "MosfetFoldedCascodeDifferentialPair",
            "MosfetCascodeAnalogInverterPmosDiodeTransistor",
            "MosfetNormalArray",
            "MosfetCascodeNMOSAnalogInverterOneDiodeTransistor",
            "MosfetCascodeAnalogInverterNmosCurrentMirrorLoad",
            "MosfetCascodedPMOSAnalogInverter",
            "MosfetCascodePMOSAnalogInverterOneDiodeTransistor",
        }
    )
    counter = {k: 0 for k in available_subcircuit_names}

    for ex in examples:
        tree = ET.parse(glob.glob(os.path.join(ex, "structure_result.xml"))[0])
        root = tree.getroot()
        subcircuits = root[1]

        all_subcircuits = []
        for sc in subcircuits:
            circuit_name = sc.attrib["name"]
            circuit_name = circuit_name[: circuit_name.find("[")]
            all_subcircuits.append(circuit_name)

            counter[circuit_name] = 1

    return 0 not in counter.values()


if __name__ == "__main__":
    import random

    for _ in range(20000):
        samples = [56, 49, 51]  # random.sample(range(1, 101), 3)
        demonstration_examples = get_demonstration_examples(samples)
        cover = check_cover(demonstration_examples)

        if cover:
            print("found")
            print(len(demonstration_examples), cover)
            print(samples)
            print(demonstration_examples)
            break
