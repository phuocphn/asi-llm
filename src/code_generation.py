from prompt_collections.rules import (
    gen_python_script,
    gen_python_script_v2,
    gen_python_script_v3,
    gen_python_script_v4,
    gen_python_script_chat_template_v4,
    update_python_script,
    gen_pythoncode_without_instruction,
)

from src.netlist import SPICENetlist
from pathlib import Path

import json
import click


from models import load_llms
from loguru import logger
from utils import ppformat, configure_logging
from langchain_core.messages import HumanMessage, AIMessage
import os

demonstration_netlists = {
    1: ["data/asi-fuboco-train/medium/55/"],
    2: [
        "data/asi-fuboco-train/small/55/",
        "data/asi-fuboco-train/medium/55/",
    ],
    4: [
        "data/asi-fuboco-train/small/77/",
        "data/asi-fuboco-train/small/55/",
        "data/asi-fuboco-train/medium/77/",
        "data/asi-fuboco-train/medium/55/",
    ],
    6: [
        "data/asi-fuboco-train/small/77/",
        "data/asi-fuboco-train/small/55/",
        "data/asi-fuboco-train/small/30/",
        "data/asi-fuboco-train/medium/77/",
        "data/asi-fuboco-train/medium/55/",
        "data/asi-fuboco-train/medium/30/",
    ],
    7: ["data/asi-fuboco-train/small/77/"],
    8: ["data/asi-fuboco-train/medium/55/"],
}


def hl2_code_generator(
    instruction_path, subcircuit_name, test_index, call_model, model, config
):
    logger.info(f"subcircuit name: {subcircuit_name}")
    logger.info(f"instruction path: {instruction_path}")

    if instruction_path is not None:
        with open(instruction_path, "r") as f:
            generated_instruction = f.read()
    else:
        generated_instruction = None

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

    template = (
        gen_python_script_chat_template_v4
        if instruction_path
        else gen_pythoncode_without_instruction
    )
    prompt = template(
        instruction=generated_instruction,
        subcircuit_name=subcircuit_name + "s",
        testcase=testcase_str,
    )

    # logger.info(prompt.invoke({}).to_string())

    if call_model:
        chat_history = []
        chain = prompt | model

        message = f"""
        **Instructions**  
        ```
        {generated_instruction}
        ```

        {testcase_str}
        """

        for i in range(config["max_retries"]):
            response = chain.invoke({"chat_history": chat_history})
            chat_history.append(HumanMessage(content=message))
            chat_history.append(AIMessage(content=response.content))
            response_path = os.path.join(
                config["working_dir"],
                f"response{i}.log",
            )

            with open(response_path, "w") as f:
                f.write(response.content)

            while True:
                user_feedback = input(f"runtime errors occured [{i}]: ")
                if user_feedback.startswith("yes") or user_feedback.startswith("no"):
                    break

            if user_feedback.startswith("yes"):
                error_path = os.path.join(
                    config["working_dir"],
                    f"error{i}.log",
                )
                if os.path.exists(error_path):
                    with open(error_path, "r") as f:
                        error_msg = f.read()
                    message = (
                        update_python_script(error_message=error_msg)
                        .invoke({})
                        .to_string()
                    )
                    logger.info(message)
            else:
                break


def hl1_code_generator(instruction_path, test_index, call_model, model, config):
    print(f"instruction path: {instruction_path}")

    if instruction_path is not None:
        with open(instruction_path, "r") as f:
            generated_instruction = f.read()
    else:
        generated_instruction = None

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
        ```{data.netlist}
        ```

        **Expected Output**  (order of list elements does not matter)  
        ```
        {ground_truth}
        ```
        ----\n
        """
        testcase_str += test

    template = (
        gen_python_script_chat_template_v4
        if instruction_path
        else gen_pythoncode_without_instruction
    )
    prompt = template(
        instruction=generated_instruction,
        subcircuit_name="diode-connected transistors and load/compensation capacitors",
        testcase=testcase_str,
    )

    if call_model:
        chat_history = []
        chain = prompt | model
        message = f"""
        **Instructions**  
        ```
        {generated_instruction}
        ```

        {testcase_str}
        """

        for i in range(config["max_retries"]):
            response = chain.invoke({"chat_history": chat_history})
            chat_history.append(HumanMessage(content=message))
            chat_history.append(AIMessage(content=response.content))
            response_path = os.path.join(
                config["working_dir"],
                f"response{i}.log",
            )

            with open(response_path, "w") as f:
                f.write(response.content)

            while True:
                user_feedback = input(f"runtime errors occured [{i}]: ")
                if user_feedback.startswith("yes") or user_feedback.startswith("no"):
                    break

            if user_feedback.startswith("yes"):
                error_path = os.path.join(
                    config["working_dir"],
                    f"error{i}.log",
                )
                if os.path.exists(error_path):
                    with open(error_path, "r") as f:
                        error_msg = f.read()
                    message = (
                        update_python_script(error_message=error_msg)
                        .invoke({})
                        .to_string()
                    )
                    logger.info(message)
            else:
                break


def hl3_code_generator(instruction_path, test_index, call_model, model, config):
    print(f"instruction path: {instruction_path}")

    if instruction_path is not None:
        with open(instruction_path, "r") as f:
            generated_instruction = f.read()
    else:
        generated_instruction = None

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

    template = (
        gen_python_script_chat_template_v4
        if instruction_path
        else gen_pythoncode_without_instruction
    )
    prompt = template(
        instruction=generated_instruction,
        subcircuit_name="amplification stages, feedback stages, load and bias parts",
        testcase=testcase_str,
    )

    # print(prompt.invoke({}).to_string())
    if call_model:
        chat_history = []
        chain = prompt | model

        message = f"""
        **Instructions**  
        ```
        {generated_instruction}
        ```

        {testcase_str}
        """

        for i in range(config["max_retries"]):
            response = chain.invoke({"chat_history": chat_history})
            chat_history.append(HumanMessage(content=message))
            chat_history.append(AIMessage(content=response.content))
            response_path = os.path.join(
                config["working_dir"],
                f"response{i}.log",
            )

            with open(response_path, "w") as f:
                f.write(response.content)

            while True:
                user_feedback = input(f"runtime errors occured [{i}]: ")
                if user_feedback.startswith("yes") or user_feedback.startswith("no"):
                    break

            if user_feedback.startswith("yes"):
                error_path = os.path.join(
                    config["working_dir"],
                    f"error{i}.log",
                )
                if os.path.exists(error_path):
                    with open(error_path, "r") as f:
                        error_msg = f.read()
                    message = (
                        update_python_script(error_message=error_msg)
                        .invoke({})
                        .to_string()
                    )
                    logger.info(message)
            else:
                break


@click.command()
@click.option(
    "--level",
    default=2,
    prompt="Hierarchical Level: ",
)
@click.option(
    "--instruction_path",
    default=None,
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
    help="should we can model invoke or just show the prompt.",
)
@click.option(
    "--model_name",
    default="llama3.3:70b",
    prompt="llm name: ",
    help="which llm is used for code generation (default: gpt-4o).",
)
def code_generator(
    level, instruction_path, subcircuit_name, test_index, call_model, model_name
):
    subcircuit_abbrev_map = {
        "Current Mirror": "CM",
        "Differential Pair": "DiffPair",
        "Inverter": "Inverter",
        "HL1": "HL1",
        "HL3": "HL3",
    }
    subcircuit = subcircuit_abbrev_map[subcircuit_name]
    if subcircuit == "HL1":
        level = 1
    elif subcircuit == "HL3":
        level = 3
    else:
        level = 2
    print(model_name, model_name)
    model = load_llms(model_name)
    if level == 2:
        name = f"{model_name}/HL2-{subcircuit}"
    else:
        name = f"{model_name}/{subcircuit}"

    if instruction_path is None:
        dirname = "direct.code"
    else:
        dirname = "instruction+code"
    working_dir = f"outputs/{dirname}/{name}"
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    configure_logging(logdir=working_dir)

    config = {
        "model_name": model_name,
        "level": level,
        "working_dir": working_dir,
        "max_retries": 20,
    }
    if level == 1:
        hl1_code_generator(instruction_path, test_index, call_model, model, config)
    if level == 2:
        hl2_code_generator(
            instruction_path, subcircuit_name, test_index, call_model, model, config
        )
    if level == 3:
        hl3_code_generator(instruction_path, test_index, call_model, model, config)


if __name__ == "__main__":
    code_generator()
