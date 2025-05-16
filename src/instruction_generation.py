import glob
import json
import os
import click
import xml.etree.ElementTree as ET
from pathlib import Path
from loguru import logger
from src.netlist import SPICENetlist
from prompt_collections.rules import (
    gen_instruction_prompt,
    gen_instruction_hl3_prompt,
    update_instruction_prompt_v2,
    gen_instruction_hl1_prompt,
)


from models import load_llms, google_genai_model
from utils import ppformat, configure_logging


def get_demonstration_examples(
    netlist_ids=[56, 49, 51], subsets=["small", "medium"], level=2
):
    all_examples = []
    subcircuit_names = set()

    for dir in subsets:
        for i in netlist_ids:
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

    if level == 2 or level == 1:
        assert len(subcircuit_names) == 21, f"#subcircuit: {len(subcircuit_names)}"
    else:
        assert len(subcircuit_names) == 6, f"#subcircuit: {len(subcircuit_names)}"
    return all_examples


def model_call(model, prompt, data: SPICENetlist) -> list[str, str]:
    try:
        if isinstance(model, google_genai_model):
            prompt_content = prompt.invoke({"netlist": data.netlist}).to_string()
            output = model.invoke(prompt_content)
        else:
            chain = prompt | model  # | parser
            output = chain.invoke({"netlist": data.netlist}).content

        parsed_data = output[
            output.find("<instruction>")
            + len("<instruction>") : output.find("</instruction>")
        ]

        return output, parsed_data
    except json.decoder.JSONDecodeError as e:
        logger.error(f"parsing LLM output failed: " + output)
        return None, None

    except Exception as e:
        logger.error(f"exception: {e}")
        return None, None


def gen_rules(model_name, subcircuit: str):
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

    if not subcircuit.startswith("HL3"):
        demonstration_examples = get_demonstration_examples(
            netlist_ids=[77, 55, 30], level=level
        )
    else:
        demonstration_examples = get_demonstration_examples(
            netlist_ids=[91, 58], subsets=["small"], level=level
        )

    logger.info(f"len of demonstration examples: {demonstration_examples}")

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
        logger.info(f"output:" + output)
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
            logger.info(f"instruction update-output:" + output)
            logger.info(f"instruction update-Parsed data: {parsed_data}")

            with open(
                os.path.join(working_dir, f"instruction-{index}-revised.md"), "w"
            ) as f:
                f.write(parsed_data)


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
