from prompt_collections.rules import (
    gen_python_script,
    gen_python_script_v2,
    gen_python_script_v3,
)
from src.netlist import SPICENetlist
import json

from models import load_openai
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
@click.option(
    "--call_model",
    default=False,
    prompt="should call model and get the output?",
    help="enable invoking model (gpt-4o).",
)
def gen_prompt(instruction_path, subcircuit_name, testcase_netlist, call_model):
    # instruction_path = "outputs/rule_accumulator/llama3.3:70b-2025-04-19_14:54:24/instruction-12-revised.md"
    # subcircuit_name = "Current Mirror"
    print(f"subcircuit name: {subcircuit_name}")
    print(f"instruction path: {instruction_path}")

    with open(instruction_path, "r") as f:
        generated_instruction = f.read()

    subcircuit_abbrev_map = {
        "Current Mirror": "CM",
        "Differential Pair": "DiffPair",
        "Inverter": "Inverter",
    }

    testcases = [
        # "data/asi-fuboco-train/small/56/",
        # "data/asi-fuboco-train/small/49/",
        "data/asi-fuboco-train/small/51/",
        # "data/asi-fuboco-train/medium/56/",
        # "data/asi-fuboco-train/medium/49/",
        # "data/asi-fuboco-train/medium/51/",
    ]
    testcase_str = ""
    for i, testcase_netlist in enumerate(testcases):
        data = SPICENetlist(testcase_netlist)

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
        test = f"""
        **Test Case {i+1}**  
        **Input SPICE Netlist**  
        ```
        {data.netlist}
        ```

        **Expected Output**  (order of list elements does not matter)  
        ```
        {ground_truth}
        ```
        ----\n
        """
        testcase_str += test

    prompt = gen_python_script_v3(
        instruction=generated_instruction,
        subcircuit_name=subcircuit_name,
        testcase=testcase_str,
    )

    print(prompt.invoke({}).to_string())
    if call_model:
        model = load_openai(model_name="gpt-4.1")
        output = (prompt | model).invoke({}).content
        print(output)


if __name__ == "__main__":
    gen_prompt()
