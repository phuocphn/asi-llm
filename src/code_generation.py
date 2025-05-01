from prompt_collections.rules import (
    gen_python_script,
    gen_python_script_v2,
    gen_python_script_v3,
    gen_python_script_v4,
)
from src.netlist import SPICENetlist
import json

from models import load_openai
import click


demonstration_netlists = {
    1: ["data/asi-fuboco-train/medium/79/"],
    2: [
        "data/asi-fuboco-train/small/79/",
        "data/asi-fuboco-train/medium/79/",
    ],
    4: [
        "data/asi-fuboco-train/small/51/",
        "data/asi-fuboco-train/small/79/",
        "data/asi-fuboco-train/medium/51/",
        "data/asi-fuboco-train/medium/79/",
    ],
    6: [
        "data/asi-fuboco-train/small/5/",
        "data/asi-fuboco-train/small/51/",
        "data/asi-fuboco-train/small/79/",
        "data/asi-fuboco-train/medium/5/",
        "data/asi-fuboco-train/medium/51/",
        "data/asi-fuboco-train/medium/79/",
    ],
}


def hl2_code_generator(instruction_path, subcircuit_name, test_index, call_model):
    print(f"subcircuit name: {subcircuit_name}")
    print(f"instruction path: {instruction_path}")

    with open(instruction_path, "r") as f:
        generated_instruction = f.read()

    subcircuit_abbrev_map = {
        "Current Mirror": "CM",
        "Differential Pair": "DiffPair",
        "Inverter": "Inverter",
    }

    testcase_str = ""
    for i, testcase in enumerate(demonstration_netlists[test_index]):
        data = SPICENetlist(testcase)

        ground_truth = str(
            json.dumps(
                [
                    (sc_name, components)
                    for sc_name, components in data.hl2_gt
                    if sc_name == subcircuit_abbrev_map[subcircuit_name]
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

    prompt = gen_python_script_v4(
        instruction=generated_instruction,
        subcircuit_name=subcircuit_name + "s",
        testcase=testcase_str,
    )

    print(prompt.invoke({}).to_string())
    if call_model:
        model = load_openai(model_name="gpt-4.1")
        output = (prompt | model).invoke({}).content
        print(output)


def gen_hl1_prompt(instruction_path, test_index, call_model):
    print(f"instruction path: {instruction_path}")

    with open(instruction_path, "r") as f:
        generated_instruction = f.read()

    testcase_str = ""
    for i, testcase_netlist in enumerate(demonstration_netlists[test_index]):
        data = SPICENetlist(testcase_netlist)

        ground_truth = str(
            json.dumps([sc for sc in data.hl1_gt])
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

    prompt = gen_python_script_v4(
        instruction=generated_instruction,
        subcircuit_name="diode-connected transistors and load/compensation capacitors",
        testcase=testcase_str,
    )

    print(prompt.invoke({}).to_string())
    if call_model:
        model = load_openai(model_name="gpt-4.1")
        output = (prompt | model).invoke({}).content
        print(output)


def gen_hl3_prompt(instruction_path, test_index, call_model):
    print(f"instruction path: {instruction_path}")

    with open(instruction_path, "r") as f:
        generated_instruction = f.read()

    testcase_str = ""
    for i, testcase_netlist in enumerate(demonstration_netlists[test_index]):
        data = SPICENetlist(testcase_netlist)

        ground_truth = str(
            json.dumps([sc for sc in data.hl3_gt])
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

    prompt = gen_python_script_v4(
        instruction=generated_instruction,
        subcircuit_name="amplification stages, feedback stages, load and bias parts",
        testcase=testcase_str,
    )

    print(prompt.invoke({}).to_string())
    if call_model:
        model = load_openai(model_name="gpt-4.1")
        output = (prompt | model).invoke({}).content
        print(output)


@click.command()
@click.option(
    "--level",
    default=2,
    prompt="Hierarchical Level: ",
)
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
    "--test_index",
    default=1,
    prompt="Test case index: ",
)
@click.option(
    "--call_model",
    default=False,
    prompt="should call model and get the output?",
    help="enable invoking model (gpt-4o).",
)
def code_generator(level, instruction_path, subcircuit_name, test_index, call_model):
    if level == 1:
        gen_hl1_prompt(instruction_path, test_index, call_model)
    if level == 2:
        hl2_code_generator(instruction_path, subcircuit_name, test_index, call_model)
    if level == 3:
        gen_hl3_prompt(instruction_path, test_index, call_model)


if __name__ == "__main__":
    code_generator()
