from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import PromptTemplate

abbreviation_mapping = {
    "First Amplification Stage": "firstStage",
    "Second Amplification Stage": "secondStage",
    "Third Amplification Stage": "thirdStage",
    "Load Parts": "loadPart",
    "Bias Parts": "biasPart",
    "Feedback Stage": "feedBack",
}


def prompt_hl3_direct_prompting_single_subcircuit(subcircuit_name="Current Mirror"):
    abbreviation = abbreviation_mapping[subcircuit_name]
    v1 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name} ({abbreviation}). "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + f"- 'sub_circuit_name': '{abbreviation}'\n"
                + f"- 'transistor_names': a list of transistor names that belong to this {subcircuit_name}\n"
                + "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    v2 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name}s (`{abbreviation}`). "
                + "Provide your output as a list of tuples. Each tuple must contain two elements:\n"
                + f"- The abbreviation string: '{abbreviation}'\n"
                + f"- A list of transistors that belong to this {subcircuit_name}\n"
                + "Wrap your response between `<result>` and `</result>` tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    v3 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name}s (`{abbreviation}`). "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + f"- 'sub_circuit_name': '{abbreviation}'\n"
                + f"- 'components': a list of component names (i.e. transistors) that belong to this {subcircuit_name}\n"
                + "Wrap your response between `<json>` and `</json>` tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return v3


def prompt_hl3_direct_prompting_single_subcircuit_with_instrucion(
    subcircuit_name="Current Mirror", instruction_src=None
):
    abbreviation = abbreviation_mapping[subcircuit_name]
    v2 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name}s (`{abbreviation}`). "
                + f"When answering the question, incorporate the provided instructions to improve the identification accuracy. "
                + "Provide your output as a list of tuples. Each tuple must contain two elements:\n"
                + f"- The abbreviation string: '{abbreviation}'\n"
                + f"- A list of transistors that belong to this {subcircuit_name}\n"
                + "Wrap your response between `<result>` and `</result>` tags. Do not include any explanation, description, or comments.\n"
                + f"Provided Identification Instructions:\n{instruction_src}\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    v3 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name}s (`{abbreviation}`). "
                + f"When answering the question, incorporate the provided instructions to improve the identification accuracy. "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + f"- 'sub_circuit_name': '{abbreviation}'\n"
                + f"- 'components': a list of component names (i.e. transistors) that belong to this {subcircuit_name}\n"
                + "Wrap your response between `<json>` and `</json>` tags. Do not include any explanation, description, or comments.\n",
                +f"Provided Identification Instructions:\n{instruction_src}\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return v3


def prompt_hl3_direct_prompting_multiple_subcircuits_with_instrucion(
    instruction_src=None,
):
    v1 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available amplification stages (`firstStage`, `secondStage`, `thirdStage`), feedback stage (`feedBack`), load parts (`loadPart`) and bias parts (`biasPart`). "
                + f"When answering the question, incorporate the provided instructions to improve the identification accuracy. "
                + "Provide your output as a list of tuples. Each tuple must contain two elements:\n"
                + f"- The first element indicates the subcircuit name in abbreviation, which must be one of the following: `firstStage`, `secondStage`, `thirdStage`, `loadPart`, `biasPart`, or `feedBack`\n"
                + f"- The second element is a list of transistors that belong to this subcircuit\n"
                + "Wrap your response between `<result>` and `</result>` tags. Do not include any explanation, description, or comments.\n"
                + f"Provided Identification Instructions:\n{instruction_src}\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    v3 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available amplification stages (`firstStage`, `secondStage`, `thirdStage`), feedback stage (`feedBack`), load parts (`loadPart`) and bias parts (`biasPart`). "
                + f"When answering the question, incorporate the provided instructions to improve the identification accuracy. "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + f"- 'sub_circuit_name': the subcircuit name in abbreviation, which must be one of the following: `firstStage`, `secondStage`, `thirdStage`, `loadPart`, `biasPart`, or `feedBack`\n"
                + f"- 'components': a list of component names (i.e. transistors) that belong to this subcircuit.\n"
                + "Wrap your response between `<json>` and `</json>` tags. Do not include any explanation, description, or comments.\n"
                + f"Provided Identification Instructions:\n{instruction_src}\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )

    return v3


def prompt_hl3_direct_prompting_multiple_subcircuits():

    v3 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available amplification stages (`firstStage`, `secondStage`, `thirdStage`), feedback stage (`feedBack`), load parts (`loadPart`) and bias parts (`biasPart`). "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + f"- 'sub_circuit_name': the subcircuit name in abbreviation, which must be one of the following: `firstStage`, `secondStage`, `thirdStage`, `loadPart`, `biasPart`, or `feedBack`\n"
                + f"- 'components': a list of component names (i.e. transistors) that belong to this subcircuit.\n"
                + "Wrap your response between `<json>` and `</json>` tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )

    return v3
