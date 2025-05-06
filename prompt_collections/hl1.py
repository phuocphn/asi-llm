from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import PromptTemplate


def prompt_hl1_direct_prompting():
    v1 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract diode-connected transistors (MosfetDiode), load capacitors (load_cap), and compensation capacitors (compensation_cap). "
                + "Provide your answer in JSON format.\n"
                + "The output should be a list of dictionaries. Each dictionary must have two keys:\n"
                + "- 'sub_circuit_name': the type of device, corresponding to one of the acronyms (MosfetDiode, load_cap, or compensation_cap)\n"
                + "- 'transistor_names': a list of transistor names that belong to this building block\n"
                + "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )

    v2 = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract diode-connected transistors (`MosfetDiode`), load capacitors (`load_cap`), and compensation capacitors (`compensation_cap`).\n"
                + "Provide your output as a list of tuples. Each tuple must contain two elements:\n"
                + "- The first element indicates the type of device, which must be one of the following: `MosfetDiode`, `load_cap`, or `compensation_cap`\n"
                + "- The second element is a list of transistor or capacitor names that belong to this building block\n"
                + "Wrap your response between `<result>` and `</result>` tags. Do not include any explanation, description, or comments.\n",
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return v2
