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
