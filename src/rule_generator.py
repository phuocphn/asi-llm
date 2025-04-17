import glob
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from calc1 import compute_cluster_metrics, average_metrics
from src.netlist import SPICENetlist
from prompt_collections.rules import (
    create_gen_rule_prompt,
    create_update_rule_prompt,
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

# -----
from loguru import logger
import sys
import datetime


# -----

rename_map = {
    "MosfetCascodedPMOSAnalogInverter": "Inverter",
    "MosfetCascodedNMOSAnalogInverter": "Inverter",
    "MosfetCascodedAnalogInverter": "Inverter",
    "MosfetCascodeAnalogInverterPmosDiodeTransistor": "Inverter",
    "MosfetCascodeAnalogInverterNmosDiodeTransistor": "Inverter",
    "MosfetCascodeNMOSAnalogInverterOneDiodeTransistor": "Inverter",
    "MosfetCascodePMOSAnalogInverterOneDiodeTransistor": "Inverter",
    "MosfetCascodePMOSAnalogInverterCurrentMirrorLoad": "Inverter",
    "MosfetCascodeNMOSAnalogInverterCurrentMirrorLoad": "Inverter",
    "MosfetCascodeAnalogInverterTwoCurrentMirrorLoads": "Inverter",
    "MosfetAnalogInverter": "Inverter",
    "MosfetDifferentialPair": "DiffPair",
    "MosfetFoldedCascodeDifferentialPair": "DiffPair",
    "MosfetCascodedDifferentialPair": "DiffPair",
    "MosfetSimpleCurrentMirror": "CM",
    "MosfetImprovedWilsonCurrentMirror": "CM",
    "MosfetCascodeAnalogInverterPmosCurrentMirrorLoad": "CM",
    "MosfetCascodeAnalogInverterNmosCurrentMirrorLoad": "CM",
    "MosfetFourTransistorCurrentMirror": "CM",
    "MosfetCascodeCurrentMirror": "CM",
    "MosfetWilsonCurrentMirror": "CM",
    "MosfetWideSwingCascodeCurrentMirror": "CM",
    "InverterPmosCurrentMirrorLoad": "CM",
    "CapacitorArray": "cap",
    "MosfetDiodeArray": "MosfetDiode",
    "MosfetNormalArray": "Mosfet",
}
rename_map = {k: 0 for k, _ in rename_map.items()}


def check_add(list_subcircuits):
    """Check if any of the subcircuits in could be used as demonstration circuits.

    :param list_subcircuits: _description_
    :return: _description_
    """
    should_add = False
    global rename_map
    for sc in list_subcircuits:
        if sc in rename_map and rename_map[sc] == 0:
            rename_map[sc] = 1
            should_add = True
    return should_add


def get_demonstration_examples():
    all_examples = []
    for dir in ["small", "medium"]:
        for i in range(1, 101):
            netlist_dir = f"data/benchmark-asi-100-train/{dir}/{i}/"
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

            if check_add(all_subcircuits):
                all_examples.append(netlist_dir)

    return all_examples


def check_cover(examples):
    flag_indicator = {
        subcircuit: 0
        for subcircuit in [
            [
                "MosfetCascodedPMOSAnalogInverter",
                "MosfetCascodedNMOSAnalogInverter",
                "MosfetCascodedAnalogInverter",
                "MosfetCascodeAnalogInverterPmosDiodeTransistor",
                "MosfetCascodeAnalogInverterNmosDiodeTransistor",
                "MosfetCascodeNMOSAnalogInverterOneDiodeTransistor",
                "MosfetCascodePMOSAnalogInverterOneDiodeTransistor",
                "MosfetCascodePMOSAnalogInverterCurrentMirrorLoad",
                "MosfetCascodeNMOSAnalogInverterCurrentMirrorLoad",
                "MosfetCascodeAnalogInverterTwoCurrentMirrorLoads",
                "MosfetAnalogInverter",
                "MosfetDifferentialPair",
                "MosfetFoldedCascodeDifferentialPair",
                "MosfetCascodedDifferentialPair",
                "MosfetSimpleCurrentMirror",
                "MosfetImprovedWilsonCurrentMirror",
                "MosfetCascodeAnalogInverterPmosCurrentMirrorLoad",
                "MosfetCascodeAnalogInverterNmosCurrentMirrorLoad",
                "MosfetFourTransistorCurrentMirror",
                "MosfetCascodeCurrentMirror",
                "MosfetWilsonCurrentMirror",
                "MosfetWideSwingCascodeCurrentMirror",
                "InverterPmosCurrentMirrorLoad",
                "CapacitorArray",
                "MosfetDiodeArray",
                "MosfetNormalArray",
            ]
        ]
    }

    for ex in examples:
        tree = ET.parse(glob.glob(os.path.join(ex, "structure_result.xml"))[0])
        root = tree.getroot()
        subcircuits = root[1]

        all_subcircuits = []
        for sc in subcircuits:
            circuit_name = sc.attrib["name"]
            circuit_name = circuit_name[: circuit_name.find("[")]
            all_subcircuits.append(circuit_name)

            flag_indicator[circuit_name] = 1

    return 0 not in flag_indicator.values()


def create_examples(demonstration_examples):
    examples = ""
    for i, netlist in enumerate(demonstration_examples):
        data = SPICENetlist(netlist)

        examples += f"\nExample {i}: \nSPICE Netlist:\n\n```\n{data.netlist}```\nGround Truth: {data.hl2_gt}"
        examples += "\n------------------------------"
    return examples


def gen_inital_rules(
    save_path="data/gen_rules/gen_rules_0_deepseek.md", examples=None, model=None
):
    chain = create_gen_rule_prompt() | model
    output = chain.invoke({"examples": create_examples(examples)})

    Path("data/gen_rules").mkdir(parents=True, exist_ok=True)
    with open(save_path, "w") as f:
        f.write(output.content)


def eval_rule(instruction, demonstration_examples, model):
    results = []
    logs = []

    for ex in demonstration_examples:
        data = SPICENetlist(ex)
        prompt = create_prompt_hl2_multiple_subcircuits_with_rule_provided_v2(
            instruction
        )
        _, parsed_data = llm_invoke(model, prompt, data)
        eval_results = compute_cluster_metrics(
            predicted=parsed_data, ground_truth=data.hl2_gt
        )
        results.append(eval_results)
        logs.append(
            {
                "netlist": data.netlist,
                "predicted": parsed_data,
                "ground_truth": data.hl2_gt,
                "eval_results": eval_results,
            }
        )

    metrics = average_metrics(results)
    return metrics, logs


if __name__ == "__main__":
    demonstration_examples = get_demonstration_examples()

    model_id = "llama3:70b"
    model = load_ollama(model_id)
    name = f"{model_id}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}"

    Path(f"data/gen_rules/{name}").mkdir(parents=True, exist_ok=True)

    log_level = "DEBUG"
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logfile = f"data/gen_rules/{name}/log.txt"
    logger.remove()  # Why does it logs duplicated message? · Issue #208 · Delgan/loguru https://github.com/Delgan/loguru/issues/208
    logger.add(
        sys.stderr,
        level=log_level,
        format=log_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(
        logfile,
        level=log_level,
        format=log_format,
        colorize=False,
        backtrace=True,
        diagnose=True,
    )

    max_avg_precision = 0
    instruction_id = 0
    best_instruction = None

    for step in range(5):
        if step == 0:
            rule_fn = f"data/gen_rules/{name}/step-{-1}-out.md"
            gen_inital_rules(rule_fn, demonstration_examples, model)
            with open(rule_fn, "r") as f:
                instruction = f.read()

        rule_fn = f"data/gen_rules/{name}/step-{step-1}-out.md"
        with open(rule_fn, "r") as f:
            instruction = f.read()

        metrics, logs = eval_rule(instruction, demonstration_examples, model)
        if metrics["Average Precision"] > max_avg_precision:
            max_avg_precision = metrics["Average Precision"]
            instruction_id = step - 1
            best_instruction = instruction

        eval_log = ""
        for i in range(len(logs)):
            logger.info("\nExample {i}: \n")
            logger.info("ground_truth: " + str(logs[i]["ground_truth"]))
            logger.info("predicted: " + str(logs[i]["predicted"]))
            logger.info("eval_results: " + str(logs[i]["eval_results"]))
            logger.info("\n------------------------------\n")

            data = SPICENetlist(demonstration_examples[i])
            eval_log += f"\nExample {i}: \n"
            eval_log += f"{data.netlist}"
            eval_log += "ground_truth: " + str(logs[i]["ground_truth"]) + "\n"
            eval_log += "predicted: " + str(logs[i]["predicted"]) + "\n"
            eval_log += "eval_results: " + str(logs[i]["eval_results"])
            eval_log += "\n------------------------------"

        prompt = create_update_rule_prompt()
        chain = prompt | model
        output = chain.invoke({"instruction": instruction, "eval_log": eval_log})
        logger.info(output.content)
        with open(f"data/gen_rules/{name}/step-{step}-out.md", "w") as f:
            f.write(output.content)

        with open(f"data/gen_rules/{name}/step-{step}-info.md", "w") as f:
            f.write("\ncurrent metrics: " + str(metrics))
            f.write("\n--------------------------------\n")
            f.write(
                prompt.invoke(
                    {"instruction": instruction, "eval_log": eval_log}
                ).to_string()
            )
            f.write("\n--------------------------------\n")
            f.write("\n\n" + eval_log)

    # ============================================
    logger.info("Using instruction id: " + str(instruction_id))
    logger.info("---------------------------")

    subset = "small"
    category = "pair"
    prediction_dir = f"data/gen_rules/{name}/subset_{subset}_{model_id}_{category}"
    metadata = {
        "subset": subset,
        "model_id": model_id,
        "category": category,
        "prediction_dir": prediction_dir,
    }

    prompt = create_prompt_hl2_multiple_subcircuits_with_rule_provided_v2(
        best_instruction
    )
    # Run the model with the best instruction
    result = average_metrics(
        identify_devices(
            subset, model, prompts=[prompt], category=category, metadata=metadata
        )
    )
    logger.info("Final result: " + str(result))
