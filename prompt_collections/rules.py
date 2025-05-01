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
    You are an experienced analog designer. You are developing an instruction on how to identify **{subcircuit_name}** in flat SPICE netlists.  
    The instruction should be in a step-by-step format and will be used by other LLMs to find **{subcircuit_name}** in new, unseen SPICE netlists.

    A labeled example is provided, consisting of a flat SPICE netlist and the corresponding ground truth:

    SPICE netlist:  
    \n{netlist}         \n

    Ground Truth:  
    In the given SPICE netlist, there are a total of {num_subcircuits} **{subcircuit_name}{postfix}**: {ground_truth_str}

    Your task is to:
    - Analyze the example to extract reusable, step-by-step instructions that can be used to identify the same **{subcircuit_name}** in new, unseen SPICE netlists.
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between `<instruction>` and `</instruction>` tags. The instruction should be general and applicable to new, unseen SPICE netlists.
    - Do not include any explanation, description, or comments related to the demonstration example.
    """
    )
    return prompt


def gen_instruction_hl3_prompt(
    netlist: str = None,
    hl3_gt: list[dict] = None,
):
    # correct format structure
    hl3_gt = {sc[0]: sc[1] for sc in hl3_gt}

    subcircuit_name = "amplification stages (first, second, third stage), feedback stage, load and bias parts"
    ground_truth = ""
    if len(hl3_gt["firstStage"]) > 0:
        ground_truth += f"- In the given SPICE netlist, there are a total of {len(hl3_gt['firstStage'])} transistor(s) belong to **the first amplification stage**: {hl3_gt['firstStage']}\n"
    if len(hl3_gt["secondStage"]) > 0:
        ground_truth += f"- In the given SPICE netlist, there are a total of {len(hl3_gt['secondStage'])} transistor(s) belong to **the second amplification stage**: {hl3_gt['secondStage']}\n"
    if "thirdStage" in hl3_gt and len(hl3_gt["thirdStage"]) > 0:
        ground_truth += f"- In the given SPICE netlist, there are a total of {len(hl3_gt['thirdStage'])} transistor(s) belong to **the third amplification stage**: {hl3_gt['thirdStage']}\n"
    if "loadPart" in hl3_gt and len(hl3_gt["loadPart"]) > 0:
        ground_truth += f"- In the given SPICE netlist, there are a total of {len(hl3_gt['loadPart'])} transistor(s) belong to **load parts**: {hl3_gt['loadPart']}\n"
    if "biasPart" in hl3_gt and len(hl3_gt["biasPart"]) > 0:
        ground_truth += f"- In the given SPICE netlist, there are a total of {len(hl3_gt['biasPart'])} transistor(s) belong to **bias parts**: {hl3_gt['biasPart']}\n"
    if "feedBack" in hl3_gt and len(len(hl3_gt["feedBack"])) > 0:
        ground_truth += f"- In the given SPICE netlist, there are a total of {len(hl3_gt['feedBack'])} transistor(s) belong to **feedback stages**: {hl3_gt['feedBack']}\n"

    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced analog designer. You are developing an instruction on how to identify **{subcircuit_name}** in flat SPICE netlists.  
    The instruction should be in a step-by-step format and will be used by other LLMs to find **{subcircuit_name}** in new, unseen SPICE netlists.

    A labeled example is provided, consisting of a flat SPICE netlist and the corresponding ground truth:

    SPICE netlist:  
    \n{netlist}         \n

    Ground Truth:  
    {ground_truth}

    Your task is to:
    - Analyze the example to extract reusable, step-by-step instructions that can be used to identify the same **{subcircuit_name}** in new, unseen SPICE netlists.
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between `<instruction>` and `</instruction>` tags. The instruction should be general and applicable to new, unseen SPICE netlists.
    - Do not include any explanation, description, or comments related to the demonstration example.
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
    You are an experienced analog designer. You are developing an instruction on how to identify **{subcircuit_name}** in flat SPICE netlists.  
    The instruction should be in a step-by-step format and will be used by other LLMs to find **{subcircuit_name}** in new, unseen SPICE netlists.

    You are given two step-by-step instructions derived from previous, different examples:

    **Instruction 1**:
    ```
    {instruction_1}
    ```

    **Instruction 2**:
    ```
    {instruction_2}
    ```
  
    Your task is to:
    - Analyze and combine these two instructions into a reusable, step-by-step instruction that can be used to identify **{subcircuit_name}** in new, unseen SPICE netlists.
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between `<instruction>` and `</instruction>` tags. The instruction should be general and applicable to new, unseen SPICE netlists.
    - Do not include any explanation, description, or comments related to the demonstration examples.
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
    You are an experienced analog designer. You are developing an instruction on how to identify **{subcircuit_name}** in flat SPICE netlists.  
    The instruction should be in a step-by-step format and will be used by other LLMs to identify **{subcircuit_name}** in new, unseen SPICE netlists.

    You are given two step-by-step instructions derived from previous, different examples:

    **Instruction 1**:
    ```
    {instruction_1}
    ```

    **Instruction 2**:
    ```
    {instruction_2}
    ```
  
    Your task is to:
    - Analyze and combine these two instructions into a reusable, step-by-step instruction that can be used to identify the same **{subcircuit_name}** in new, unseen SPICE netlists.
    - Do not include any duplicated information in the new instruction (e.g., duplicate steps).
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between `<instruction>` and `</instruction>` tags. The instruction should be general and easy for other large language models to follow when applied to new, unseen SPICE netlists.
    - Do not include any explanation, description, or comments related to the demonstration examples.
    """
    )
    return prompt


def gen_python_script(
    subcircuit_name: str = "Current Mirror",
    instruction: str = None,
    testcase_netlist: str = None,
    testcase_expected: str = None,
):
    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced Python programmer working on identifying **{subcircuit_name}s** in a SPICE netlist.  
    Your task is to convert the following instruction for identifying **{subcircuit_name}s** into a Python script.  
    The goal is to extract a list of all available **{subcircuit_name}s** from a new, unseen SPICE netlist.

    **Instruction**  
    ```
    {instruction}
    ```

    **Test Case**  
    **Input SPICE Netlist**  
    ```
    {testcase_netlist}
    ```

    **Expected Output**  (order of list elements does not matter)  
    ```
    {testcase_expected}
    ```
    """
    )
    return prompt


def gen_python_script_v2(
    subcircuit_name: str = "Current Mirror",
    instruction: str = None,
    testcase: str = None,
):
    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced Python programmer working on identifying **{subcircuit_name}s** in a SPICE netlist.  
    Your task is to convert the following instruction for identifying **{subcircuit_name}s** into a Python script.  
    The goal is to extract a list of all available **{subcircuit_name}s** from a new, unseen SPICE netlist.
    For each test case, make sure the returned output matches expected output.

    **Instruction**  
    ```
    {instruction}
    ```

    {testcase}
    
    Let's think step by step.
    """
    )
    return prompt


def gen_python_script_v3(
    subcircuit_name: str = "Current Mirror",
    instruction: str = None,
    testcase: str = None,
):
    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced Python programmer working on identifying **{subcircuit_name}s** in a SPICE netlist.  
    You are given the following step-by-step instruction on how to identify **{subcircuit_name}s** in a SPICE netlist.

    **Instruction**  
    ```
    {instruction}
    ```

    {testcase}
    
    Your task is to:
    - Convert the given instruction for identifying **{subcircuit_name}s** into a Python script.  
    - The generated Python script should extract a list of all available **{subcircuit_name}s** from a new, unseen SPICE netlist.
    - For each given test case, write an assertion to ensure the returned output matches the expected output.

    Let's think step by step.
    """
    )
    return prompt


def gen_python_script_v4(
    subcircuit_name: str = "Current Mirrors",
    instruction: str = None,
    testcase: str = None,
):
    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced Python programmer working on identifying **{subcircuit_name}** in a SPICE netlist.  
    You are given the following step-by-step instructions on how to identify **{subcircuit_name}** in a SPICE netlist.

    **Instructions**  
    ```
    {instruction}
    ```

    {testcase}
    
    Your task is to:
    - Translate the given instructions for identifying **{subcircuit_name}** into a Python script.  
    - The generated Python script should extract a list of all available **{subcircuit_name}** from a new, unseen SPICE netlist.
    - The generated Python script should follow the function template below:

        ```python
        def findSubCircuit(netlist: str): 
            \"\"\"
            Find all {subcircuit_name} subcircuits.

            Args:
                netlist (str): A flat SPICE netlist as a string, where each line defines a component and its connections in the circuit.

            Returns:
                List of tuples containing identified subcircuit names and the corresponding transistors.
            \"\"\"
            # add your code here
        ```

    - For each given test case, write an assertion to ensure the returned output matches the expected output.
    - In addition to the assertion, print the expected output, actual output, and any relevant information to assist in debugging if the result is not as expected.

    Let's think step by step.
    """
    )
    return prompt


def gen_instruction_hl1_prompt(
    netlist: str = None,
    hl1_gt: list[dict] = None,
):
    num_diode_connected_trans = 0
    num_load_caps = 0
    num_compensation_caps = 0
    for group in hl1_gt:
        if group[0] == "MosfetDiode":
            num_diode_connected_trans = len(group[1])
        if group[0] == "load_cap":
            num_load_caps = len(group[1])
        if group[0] == "compensation_cap":
            num_compensation_caps = len(group[1])

    if num_diode_connected_trans > 1:
        postfix_diode_connected_tran = "s"
    else:
        postfix_diode_connected_tran = ""

    ground_truth_diode_connected_trans_str = ", ".join(
        [str(d[1]) for d in hl1_gt if d[0] == "MosfetDiode"]
    )
    # ---

    if num_load_caps > 1:
        postfix_load_caps = "s"
    else:
        postfix_load_caps = ""

    ground_truth_load_caps = ", ".join(
        [str(d[1]) for d in hl1_gt if d[0] == "load_cap"]
    )

    # ---
    if num_compensation_caps > 1:
        postfix_compensation_caps = "s"
    else:
        postfix_compensation_caps = ""

    ground_truth_compensation_caps_str = ", ".join(
        [str(d[1]) for d in hl1_gt if d[0] == "compensation_cap"]
    )

    prompt = PromptTemplate.from_template(
        f"""
    You are an experienced analog designer. You are developing an instruction on how to identify diode-connected transistors and load/compensation capacitors in flat SPICE netlists.  
    The instruction should be in a step-by-step format and will be used by other LLMs to find diode-connected transistors and load/compensation capacitors in new, unseen SPICE netlists.

    A labeled example is provided, consisting of a flat SPICE netlist and the corresponding ground truth:

    SPICE netlist:  
    \n{netlist}         \n

    Ground Truth:  
    - In the given SPICE netlist, there are a total of {num_diode_connected_trans} **diode-connected transistor{postfix_diode_connected_tran}**: {ground_truth_diode_connected_trans_str}
    - In the given SPICE netlist, there are a total of {num_load_caps} **load capacitor{postfix_load_caps}**: {ground_truth_load_caps}
    - In the given SPICE netlist, there are a total of {num_compensation_caps} **compensation capacitor{postfix_compensation_caps}**: {ground_truth_compensation_caps_str}

    Your task is to:
    - Analyze the example to extract reusable, step-by-step instructions that can be used to identify diode-connected transistors and load/compensation capacitors in new, unseen SPICE netlists.
    - Use a clear, step-by-step format in Markdown, and wrap the generated instruction between `<instruction>` and `</instruction>` tags. The instruction should be general and applicable to new, unseen SPICE netlists.
    - Do not include any explanation, description, or comments related to the demonstration example.
    """
    )
    return prompt


def update_python_script(
    error_message: str = "Traceback Error: ....",
):
    prompt = PromptTemplate.from_template(
        f"""
    When I executed the provided Python code, I got the following error message:

    **Error Message**  
    ```
    {error_message}
    ```

    
    Your task is to fix any bugs, wrong logics in the previous generated Python code, so that the returned output matches the expected output.
    Let's think step by step.
    """
    )
    return prompt
