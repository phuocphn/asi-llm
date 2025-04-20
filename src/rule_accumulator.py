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
from collections import defaultdict


def get_demonstration_examples(samples=[56, 49, 51]):
    all_examples = []
    subcircuit_names = set()

    for dir in ["small", "medium"]:
        for i in samples:  # range(1, 101):
            netlist_dir = f"data/asi-fuboco-train/{dir}/{i}/"
            tree = ET.parse(
                glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0]
            )
            root = tree.getroot()
            subcircuits = root[1]

            for sc in subcircuits:
                subcircuit_name = sc.attrib["name"]
                subcircuit_name = subcircuit_name[: subcircuit_name.find("[")]
                subcircuit_names.add(subcircuit_name)
            all_examples.append(netlist_dir)

    assert len(subcircuit_names) == 21, f"number of subcircuit: {len(subcircuit_names)}"
    return all_examples


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


def model_call(model, prompt, data: SPICENetlist) -> list[str, str]:
    try:
        chain = prompt | model  # | parser
        output = chain.invoke({"netlist": data.netlist})
        parsed_data = output.content[
            output.content.find("<instruction>")
            + len("<instruction>") : output.content.find("</instruction>")
        ]

        return output, parsed_data
    except json.decoder.JSONDecodeError as e:
        logger.error(f"parsing LLM output failed: " + output.content)
        return None, None

    except Exception as e:
        logger.error(f"exception: {e}")
        return None, None


if __name__ == "__main__":
    demonstration_examples = get_demonstration_examples()

    logger.info(f"len of demonstration examples: {demonstration_examples}")
    model_id = "llama3.3:70b"
    model = load_ollama(model_id)
    name = f"{model_id}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}"

    working_dir = f"outputs/rule_accumulator/{name}"
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    configure_logging(logdir=working_dir)
    log_level = "DEBUG"

    subcircuit = "Inverter"
    instruction = f"Generate a rule for {subcircuit} subcircuits"
    logger.info(f"Instruction: {instruction}")

    subcircuit_abbrev_map = {
        "Current Mirror": "CM",
        "Differential Pair": "DiffPair",
        "Inverter": "Inverter",
    }

    for index, ex in enumerate(demonstration_examples):
        data = SPICENetlist(ex)

        ground_truth = [
            sc["transistor_names"]
            for sc in data.hl2_gt
            if sc["sub_circuit_name"] == subcircuit_abbrev_map[subcircuit]
        ]

        prompt = gen_instruction_prompt(
            subcircuit_name=subcircuit,
            netlist=data.netlist,
            ground_truth=ground_truth,
        )
        logger.info(prompt.invoke({}).to_string())

        output, parsed_data = model_call(model, prompt, data)
        logger.info(f"output:" + output.content)
        logger.info(f"Parsed data: {parsed_data}")

        with open(os.path.join(working_dir, f"instruction-{index}.md"), "w") as f:
            f.write(parsed_data)

        if index > 0:
            logger.info("Update instruction")

            if index == 1:
                fn = f"instruction-{index-1}.md"
            else:
                fn = f"instruction-{index-1}-revised.md"
            with open(os.path.join(working_dir, fn), "r") as f:
                prev_instruction = f.read()

            prompt = update_instruction_prompt_v2(
                subcircuit_name=subcircuit,
                instruction_1=prev_instruction,
                instruction_2=parsed_data,
            )
            output, parsed_data = model_call(model, prompt, data)
            logger.info(f"instruction update-output:" + output.content)
            logger.info(f"instruction update-Parsed data: {parsed_data}")

            with open(
                os.path.join(working_dir, f"instruction-{index}-revised.md"), "w"
            ) as f:
                f.write(parsed_data)

    with open(os.path.join(working_dir, f"instruction-{index}-revised.md"), "r") as f:
        final_generated_instruction = f.read()
