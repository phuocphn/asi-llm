from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate


def create_gen_rule_prompt():
    """The prompt for generating instructions and rules for identifying analog subcircuits in flat SPICE netlists without Chain-of-Thought."""

    prompt = PromptTemplate.from_template(
        """
    You are given a set of labeled examples consisting of flat SPICE netlists and corresponding ground truth subcircuit annotations. Each ground truth identifies functional analog blocks (e.g., Differential Pair, Current Mirror, Inverter) as a dictionary with a `subsub_circuit_name` and a list of transistor `transistor_names` (MOSFETs, prefixed with "m").
    Analyze the examples to extract reusable identification rules or instructions that can be used to recognize the same subcircuits in new netlists.

    Examples: 

    \n{examples}         \n
    Based on these examples, generate a set of identification instructions or rules that describe how to identify:

    - A Differential Pair (DiffPair)
    - A Current Mirror (CM)
    - Inverter (Inverter)

    Use a clear, step-by-step format in Markdown. The rules should be general and apply to unseen netlists. Make sure they reference topological or structural properties of the transistors.
    Don't include any explanation, description, or comments related to demonstration examples. 
    """
    )
    return prompt


def create_update_rule_prompt():
    """The prompt for updating instructions and rules without Chain-of-Thought."""

    prompt = PromptTemplate.from_template(
        """
    You are an experienced analog circuit designer. You are developing a set of instructions and rules that large language models need to follow when identifying analog subcircuits in flat SPICE netlists.

    - A Differential Pair (DiffPair)
    - A Current Mirror (CM)
    - Inverter (Inverter)

    Below, for each example, you are given:

    - A flat SPICE netlist.
    - The current identification instruction and rules.
    - The subcircuits predicted using the current identification rules (e.g., DiffPair, CM, Inverter).
    - The ground-truth subcircuits.
    - Evaluation metrics (precision, recall, F1 score) betwwen ground-truth and predicted subcircuits.

    Current Identification Instructions and Rules:
    ```
    {instruction}
    ```

    Evaluation Logs:
    ```
    {eval_log}
    ```
    \n

    Your task is to:

    - Analyze the discrepancies between predicted and ground-truth subcircuits.
    - Identify likely causes of false positives and false negatives.
    - Propose an improved version of the identification instruction and rules that addresses the observed issues.

    Output only the revised instructions and rules in Markdown format. 
    Do not include any explanation, description, or comments about the revised and previous version. Do not include any examples or evaluation logs. Do not use the world "revised", "improved", "updated" or similar words in our output.
    """
    )
    return prompt


def create_gen_rule_prompt_per_subcircuit(
    netlist: str, ground_truth: list[dict], subcircuit_name: str = "Differrent Pair"
):
    num_subcircuits = len(ground_truth)
    if num_subcircuits > 1:
        postfix = "s"
    else:
        postfix = ""
    ground_truth_str = ", ".join([str(subcircuit) for subcircuit in ground_truth])

    """Prompt for generating instructions and rules for identifying **single** analog subcircuit in flat SPICE netlists."""
    prompt = PromptTemplate.from_template(
        f"""
    Instruction:  You are an experienced analog designer. Given a SPICE netlist and ground truth, your task is to systematically analyse the connections of all transistors in the netlist. After that, derive definition, a set of connection rules, and procedure in step-by-step for identifying {subcircuit_name}s. These rules and identification procedure  will be used later as an input for LLMs to find differential pairs in new SPICE netlists.

    **Input SPICE Netlist**
    {netlist}
    **Ground Truth**

    In the given SPICE netlist, there are a total of {num_subcircuits} **{subcircuit_name}{postfix}**:: {ground_truth_str}
    Let's think step by step
    """
    )
    return prompt


def gen_instruction_prompt(
    subcircuit_name: str = "Current Mirror",
    netlist: str = None,
    ground_truth: list[dict] = None,
):
    num_subcircuits = len(ground_truth)
    if num_subcircuits > 1:
        postfix = "s"
    else:
        postfix = ""
    ground_truth_str = ", ".join([str(subcircuit) for subcircuit in ground_truth])

    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced analog designer. You are developing a instruction of how to identify {subcircuit_name} in flat SPICE netlists.
    The instruction should be in a step-by-step format and will be used for other LLMs to find {subcircuit_name} in new unseen SPICE netlists.
    
    Given is a labeled example consisting of flat SPICE netlists and corresponding ground truth 

    SPICE netlist: 
    \n{netlist}         \n

    Ground Truth:
    In the given SPICE netlist, there are a total of {num_subcircuits} **{subcircuit_name}{postfix}**:: {ground_truth_str}

    Your task is to:
    - Analyze the example to extract reusable step-by-step instructions that can be used to identify the same {subcircuit_name} in new unseen SPICE netlists.
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between <instruction> and </instruction> tags. The instruction should be general and apply to new unseen SPICE netlists. 
    - Don't include any explanation, description, or comments related to demonstration examples. 
  
    """
    )
    return prompt


def update_instruction_prompt(
    subcircuit_name: str = "Current Mirror",
    instruction_1: str = None,
    instruction_2: str = None,
):

    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced analog designer. You are developing a instruction of how to identify {subcircuit_name} in flat SPICE netlists.
    The instruction should be in a step-by-step format and will be used for other LLMs to find {subcircuit_name} in new unseen SPICE netlists.
    
    You are given two step-by-step instructions derived from the previous different examples:

    **Instruction 1**:
    ```
    {instruction_1}
    ```

    **Instruction 2**:
    ```
    {instruction_2}
    ```
  
    Your task is to:
    - Analyze and combined these two instructions into a reusable step-by-step instruction that can be used to identify the same {subcircuit_name} in new unseen SPICE netlists.
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between <instruction> and </instruction> tags. The instruction should be general and apply to new unseen SPICE netlists. 
    - Don't include any explanation, description, or comments related to demonstration examples. 
  
    """
    )
    return prompt


def update_instruction_prompt_v2(
    subcircuit_name: str = "Current Mirror",
    instruction_1: str = None,
    instruction_2: str = None,
):

    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced analog designer. You are developing a instruction of how to identify {subcircuit_name} in flat SPICE netlists.
    The instruction should be in a step-by-step format and will be used for other LLMs to find {subcircuit_name} in new unseen SPICE netlists.
    
    You are given two step-by-step instructions derived from the previous different examples:

    **Instruction 1**:
    ```
    {instruction_1}
    ```

    **Instruction 2**:
    ```
    {instruction_2}
    ```
  
    Your task is to:
    - Analyze and combined these two instructions into a reusable step-by-step instruction that can be used to identify the same {subcircuit_name} in new unseen SPICE netlists.
    - Don't include any duplicated information in the new instruction (e.g. duplicated step).
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between <instruction> and </instruction> tags. The instruction should be general and easy to follow by other large language models when applying to new unseen SPICE netlists. 
    - Don't include any explanation, description, or comments related to demonstration examples. 
  
    """
    )
    return prompt
