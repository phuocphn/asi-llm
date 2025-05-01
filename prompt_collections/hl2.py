from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import PromptTemplate


def create_prompt_hl2():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. "
                + "Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), and Simple or Cascoded Analog Inverter (Inverter).\n"
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)\n"
                + "- 'transistor_names': a list of transistor names that belong to this building block\n"
                + "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt


def create_prompt_hl2_multiple_subcircuits_with_rule_provided(
    instruction,
):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify the following functional building blocks: Differential Pair (DiffPair), Current Mirror (CM), and Simple or Cascoded Analog Inverter (Inverter).\n"
                + f"When answering the question, use the provided definition, connection rules, and procedure to identify these functional building blocks. "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)\n"
                + "- 'transistor_names': a list of transistor names that belong to this building block\n"
                + "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n\n"
                + f"Instructions:\n ```{instruction}```",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt


def create_prompt_hl2_multiple_subcircuits_with_rule_provided_v2(
    instruction,
):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify the following functional building blocks: Differential Pair (DiffPair), Current Mirror (CM), and Simple or Cascoded Analog Inverter (Inverter).\n"
                + f"When answering the question, try to incorporate the provided instruction to correctly identify these functional building blocks. "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)\n"
                + "- 'transistor_names': a list of transistor names that belong to this building block\n"
                + "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n\n"
                + f"Provided Instructions:\n ```{instruction}```",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt


def create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided(
    instruction_src: str = None,
):
    """The prompt for identifying multiple subcircuits in flat SPICE netlists with fixed rules provided.
    Default: the instruction is loaded from docs/kb_from_grok.
    """

    if instruction_src is None:
        instruction = f"{get_knowledge_base()['DiffPair']}\n {get_knowledge_base()['CM']} \n {get_knowledge_base()['Inverter']}"
    else:
        with open(instruction_src, "r") as f:
            instruction = f.read()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify the following functional building blocks: Differential Pair (DiffPair), Current Mirror (CM), and Simple or Cascoded Analog Inverter (Inverter).\n"
                + f"When answering the question, incorporate the provided instructions and rules to improve the identification accuracy. "
                + "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n"
                + "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)\n"
                + "- 'transistor_names': a list of transistor names that belong to this building block\n"
                + "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n\n"
                + f"Provided Instructions and Rules:\n ```\n{instruction}\n```\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt


def create_prompt_hl2_with_target_single_subcircuit_only(
    subcircuit_name="Current Mirror", abbreviation="CM"
):
    prompt = ChatPromptTemplate.from_messages(
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
    return prompt
