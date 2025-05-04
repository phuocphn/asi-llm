import glob
import json
import os
import datetime
import click
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger
from calc1 import compute_cluster_metrics, average_metrics
from src.netlist import SPICENetlist
from prompt_collections.rules import (
    create_gen_rule_prompt,
    gen_instruction_prompt,
    gen_instruction_hl3_prompt,
    update_instruction_prompt_v2,
    gen_instruction_hl1_prompt,
)

from prompt_collections.hl2 import (
    create_prompt_hl2_multiple_subcircuits_with_rule_provided_v2,
)

from models import load_llms
from utils import ppformat, configure_logging


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


def llm_invoke(model, prompt, data: SPICENetlist) -> list[str, str]:
    try:
        # prompt = create_prompt_hl2()
        logger.info(prompt.invoke(data.netlist).to_string())
        chain = prompt | model  # | parser
        output = chain.invoke({"netlist": data.netlist})
        parsed_data = json.loads(
            output.content[
                output.content.find("<json>")
                + len("<json>") : output.content.find("</json>")
            ]
        )
        assert isinstance(parsed_data, list), "parsed data is not a list: " + str(
            parsed_data
        )
        return output, parsed_data
    except json.decoder.JSONDecodeError as e:
        logger.error(f"parsing LLM output failed: " + output.content)
        return None, None

    except Exception as e:
        logger.error(f"exception: {e}")
        return None, None


# @click.command()
# @click.option(
#     "--model_name",
#     default="gpt-4.1",
#     help="the LLM is used for instruction generation stage",
# )
# @click.option(
#     "--subcircuit",
#     default="HL1",
#     prompt="which is the target subcircuit ?",
#     help="which is the target subcircuit ?",
#     type=click.Choice(
#         ["HL1", "Current Mirror", "Differential Pair", "Inverter", "HL3"],
#         case_sensitive=True,
#     ),
# )
def gen_rules(model_name, subcircuit):
    demonstration_examples = get_demonstration_examples([77, 55, 30])

    logger.info(f"len of demonstration examples: {demonstration_examples}")
    subcircuit_abbrev_map = {
        "Current Mirror": "CM",
        "Differential Pair": "DiffPair",
        "Inverter": "Inverter",
        "HL1": "HL1",
        "HL3": "HL3",
    }
    if subcircuit == "HL1":
        level = 1
    elif subcircuit == "HL3":
        level = 3
    else:
        level = 2

    model = load_llms(model_name)
    if level == 2:
        name = f"{model_name}/HL2-{subcircuit_abbrev_map[subcircuit]}"
    else:
        name = f"{model_name}/{subcircuit_abbrev_map[subcircuit]}"

    working_dir = f"outputs/instruction_generation/{name}"
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    configure_logging(logdir=working_dir)

    instruction = f"Generate a rule for {subcircuit} subcircuits"
    logger.info(f"Instruction: {instruction}")

    for index, ex in enumerate(demonstration_examples):
        data = SPICENetlist(ex)

        if level == 1:
            prompt = gen_instruction_hl1_prompt(
                netlist=data.netlist, hl1_gt=data.hl1_gt
            )
            # prompt_fn = gen_instruction_hl1_prompt  # or gen_instruction_prompt
        elif level == 2:
            ground_truth = [
                components
                for sc_name, components in data.hl2_gt
                if sc_name == subcircuit_abbrev_map[subcircuit]
            ]
            prompt = gen_instruction_prompt(
                subcircuit_name=subcircuit,
                netlist=data.netlist,
                ground_truth=ground_truth,
            )
        elif level == 3:
            prompt = gen_instruction_hl3_prompt(
                netlist=data.netlist,
                hl3_gt=data.hl3_gt,
            )

        logger.info(prompt.invoke({}).to_string())

        output, parsed_data = model_call(model, prompt, data)
        # logger.info(f"output:" + output.content)
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

            if level == 1:
                subcircuit_name = (
                    "diode-connected transistors and load/compensation capacitors"
                )
            elif level == 2:
                subcircuit_name = subcircuit
            elif level == 3:
                subcircuit_name = "amplification stages (first, second, third stage), feedback stage, load and bias parts"

            prompt = update_instruction_prompt_v2(
                subcircuit_name=subcircuit_name,
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

    # with open(os.path.join(working_dir, f"instruction-{index}-revised.md"), "r") as f:
    #     final_generated_instruction = f.read()


@click.command()
@click.option(
    "--model_name",
    default="gpt-4.1",
    help="the LLM is used for instruction generation stage",
)
def gen_all_rules(model_name):
    for subcircuit in ["HL1", "Differential Pair", "Current Mirror", "Inverter", "HL3"]:
        gen_rules(model_name, subcircuit)


if __name__ == "__main__":
    gen_all_rules()
