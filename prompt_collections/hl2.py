from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import PromptTemplate

abbreviation_mapping = {
    "Differential Pair": "DiffPair",
    "Current Mirror": "CM",
    "Inverter": "Inverter",
}


def prompt_hl2_direct_prompting_single_subcircuit(subcircuit_name="Current Mirror"):
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

    return v2


def prompt_hl2_direct_prompting_single_subcircuit_with_instrucion(
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

    return v2
