from prompt_collections.rules import gen_python_script
from src.netlist import SPICENetlist
import json


import click


@click.command()
@click.option(
    "--instruction_path",
    default="/tmp/abc.txt",
    help="path to the markdown instruction file.",
)
@click.option(
    "--subcircuit_name",
    default="Current Mirror",
    prompt="subcircuit name",
    help="subcircuit name.",
)
@click.option(
    "--testcase_netlist",
    default="data/asi-fuboco-train/medium/56",
    prompt="Test case netlist",
    help="subcircuit name.",
)
def gen_prompt(instruction_path, subcircuit_name, testcase_netlist):
    # instruction_path = "outputs/rule_accumulator/llama3.3:70b-2025-04-19_14:54:24/instruction-12-revised.md"
    # subcircuit_name = "Current Mirror"
    print(f"subcircuit name: {subcircuit_name}")
    print(f"instruction path: {instruction_path}")
    data = SPICENetlist(testcase_netlist)

    with open(instruction_path, "r") as f:
        generated_instruction = f.read()

    subcircuit_abbrev_map = {
        "Current Mirror": "CM",
        "Differential Pair": "DiffPair",
        "Inverter": "Inverter",
    }

    ground_truth = str(
        json.dumps(
            [
                # {"sub_circuit_name": "CM", "transistor_names": sc["transistor_names"]}
                sc
                for sc in data.hl2_gt
                if sc["sub_circuit_name"] == subcircuit_abbrev_map[subcircuit_name]
            ]
        )
        .replace('"', "'")
        .replace("{", "{{")
        .replace("}", "}}")
    )

    prompt = gen_python_script(
        instruction=generated_instruction,
        subcircuit_name=subcircuit_name,
        testcase_netlist=data.netlist,
        testcase_expected=ground_truth,
    )

    print(prompt.invoke({}).to_string())


if __name__ == "__main__":
    gen_prompt()
