from prompt_collections.rules import (
    gen_python_script,
    gen_python_script_v2,
    gen_python_script_v3,
    gen_python_script_v4,
    gen_python_script_chat_template_v4,
    gen_python_script_chat_template_v5,
    gen_pythoncode_without_instruction_v5,
    update_python_script,
    update_python_script_v2,
    gen_pythoncode_without_instruction,
)

from src.netlist import SPICENetlist
from src.code_execution import parse_and_execute_python_code
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
    9: ["data/asi-fuboco-train/small/58/"],
    10: ["data/asi-fuboco-train/small/91/"],
    11: ["data/asi-fuboco-train/small/91/", "data/asi-fuboco-train/small/58/"],
}


def code_fixing(prompt, model, config):
    chain = prompt | model
    message = None

    chat_history = []
    for i in range(config["max_retries"]):
        response = chain.invoke({"chat_history": chat_history})
        chat_history.append(AIMessage(content=response.content))
        response_path = os.path.join(
            config["working_dir"],
            f"response_{i}.log",
        )
        code_path = os.path.join(
            config["working_dir"],
            f"code_{i}.py",
        )
        error_path = os.path.join(
            config["working_dir"],
            f"error_{i}.log",
        )
        with open(response_path, "w") as f:
            f.write(response.content)

        success, code, error_msg = parse_and_execute_python_code(response_path)

        with open(code_path, "w") as f:
            f.write(code)
        with open(error_path, "w") as f:
            f.write(error_msg)

        if success:
            logger.info("All assertions passed.")
            return chat_history

        # Escape `{` and `}` in code and error_msg
        escaped_error_msg = error_msg.replace("{", "{{").replace("}", "}}")
        escaped_code = code.replace("{", "{{").replace("}", "}}")
        message = update_python_script(escaped_error_msg).invoke({}).to_string()
        logger.info(message)
        if message:
            chat_history.append(HumanMessage(content=message))

    return chat_history


def hl1_code_generator(instruction_path, test_index, call_model, model, config):
    print(f"instruction path: {instruction_path}")

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

    if instruction_path:
        with open(instruction_path, "r") as f:
            generated_instruction = f.read()
        prompt = gen_python_script_chat_template_v4(
            instruction=generated_instruction,
            subcircuit_name="diode-connected transistors and load/compensation capacitors",
            testcase=testcase_str,
        )
    else:
        prompt = gen_pythoncode_without_instruction_v5(
            subcircuit_name="diode-connected transistors and load/compensation capacitors",
            testcase=testcase_str,
        )

    print(prompt.invoke({"chat_history": []}).to_string())
    if call_model:
        chat_history = code_fixing(prompt, model, config)
        history_logfile = os.path.join(
            config["working_dir"],
            f"chat_history.log",
        )
        with open(history_logfile, "w") as f:
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    f.write(f"User: {message.content}\n")
                elif isinstance(message, AIMessage):
                    f.write(f"AI: {message.content}\n")
                else:
                    f.write(f"Unknown message type: {message}\n")
        logger.info(f"Chat history saved to {history_logfile}")


def hl2_code_generator(
    instruction_path, subcircuit_name, test_index, call_model, model, config
):
    logger.info(f"subcircuit name: {subcircuit_name}")
    logger.info(f"instruction path: {instruction_path}")

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

    if instruction_path:
        with open(instruction_path, "r") as f:
            generated_instruction = f.read()
        prompt = gen_python_script_chat_template_v4(
            instruction=generated_instruction,
            subcircuit_name=subcircuit_name + "s",
            testcase=testcase_str,
        )
    else:
        prompt = gen_pythoncode_without_instruction_v5(
            subcircuit_name=subcircuit_name + "s",
            testcase=testcase_str,
        )

    print(prompt.invoke({"chat_history": []}).to_string())
    if call_model:
        chat_history = code_fixing(prompt, model, config)
        history_logfile = os.path.join(
            config["working_dir"],
            f"chat_history.log",
        )
        with open(history_logfile, "w") as f:
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    f.write(f"User: {message.content}\n")
                elif isinstance(message, AIMessage):
                    f.write(f"AI: {message.content}\n")
                else:
                    f.write(f"Unknown message type: {message}\n")
        logger.info(f"Chat history saved to {history_logfile}")


def hl3_code_generator(instruction_path, test_index, call_model, model, config):
    print(f"instruction path: {instruction_path}")

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

    if instruction_path:
        with open(instruction_path, "r") as f:
            generated_instruction = f.read()
        prompt = gen_python_script_chat_template_v4(
            instruction=generated_instruction,
            subcircuit_name="amplification stages, feedback stages, load and bias parts",
            testcase=testcase_str,
        )
    else:
        prompt = gen_pythoncode_without_instruction_v5(
            subcircuit_name="amplification stages, feedback stages, load and bias parts",
            testcase=testcase_str,
        )

    print(prompt.invoke({"chat_history": []}).to_string())
    if call_model:
        chat_history = code_fixing(prompt, model, config)
        history_logfile = os.path.join(
            config["working_dir"],
            f"chat_history.log",
        )
        with open(history_logfile, "w") as f:
            for message in chat_history:
                if isinstance(message, HumanMessage):
                    f.write(f"User: {message.content}\n")
                elif isinstance(message, AIMessage):
                    f.write(f"AI: {message.content}\n")
                else:
                    f.write(f"Unknown message type: {message}\n")
        logger.info(f"Chat history saved to {history_logfile}")


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

    instruction_dir = {
        "Differential Pair": "HL2-DiffPair",
        "Current Mirror": "HL2-CM",
        "Inverter": "HL2-Inverter",
        "HL1": "HL1",
        "HL3": "HL3",
    }

    for subcircuit_name in subcircuit_abbrev_map.keys():

        subcircuit = subcircuit_abbrev_map[subcircuit_name]
        instruction_path = os.path.join(
            "outputs",
            "instruction_generation",
            model_name,
            instruction_dir[subcircuit_name],
            "instruction-5-revised.md",
        )

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
            dirname = "direct+code"
        else:
            dirname = "w.instruction+code"
        working_dir = f"outputs/{dirname}/{name}"
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        configure_logging(logdir=working_dir)

        config = {
            "model_name": model_name,
            "level": level,
            "working_dir": working_dir,
            "max_retries": 5 + 1,
            # "max_retries": 20 + 1,
        }
        if level == 1:
            hl1_code_generator(instruction_path, test_index, call_model, model, config)
        elif level == 2:
            hl2_code_generator(
                instruction_path, subcircuit_name, test_index, call_model, model, config
            )
        elif level == 3:
            hl3_code_generator(instruction_path, test_index, call_model, model, config)
        else:
            raise ValueError("level should be 1, 2 or 3.")


if __name__ == "__main__":
    code_generator()
