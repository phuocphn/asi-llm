from src.netlist import SPICENetlist
import glob 
import os
import xml.etree.ElementTree as ET

from pathlib import Path
import transformers
import torch
import os
import json

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import  ChatOllama
from langchain_openai import ChatOpenAI

from calc1 import compute_cluster_metrics, compute_cluster_metrics_hl1, average_metrics
from src.netlist import SPICENetlist
from src.kb import get_knowledge_base
import hydra
from omegaconf import DictConfig, OmegaConf
from main import  llm_invoke


#-----
from loguru import logger
import sys
import datetime
from langchain_openai.chat_models.base import BaseChatOpenAI

log_level = "DEBUG"
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logfile = f"logs/rule_generator/{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.txt"
logger.remove() #Why does it logs duplicated message? · Issue #208 · Delgan/loguru https://github.com/Delgan/loguru/issues/208
logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
logger.add(logfile, level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)


def load_ollama(model_id="deepseek-r1:70b"):
    logger.info (f"use ollama with model id: {model_id}")
    llm = ChatOllama(model=model_id, 
                        temperature = 0.0,
                        max_tokens = 15000, #4096
                        device=0
                    )
    return llm

def loadopenai():
    model_id = "gpt-4o"
    openai_api_key=os.getenv('OPENAI_API_KEY', None)
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    llm = ChatOpenAI(
        model=model_id,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=openai_api_key,
    )
    logger.info (f"use openai with model id: {model_id}" )
    return llm

def deepseek():
    model = BaseChatOpenAI(
        model='deepseek-reasoner', 
        openai_api_key='DEEPSEEK_API_KEY', 
        openai_api_base='https://api.deepseek.com',
        max_tokens=8192, 
    )
    return model


rename_map = {
	'MosfetCascodedPMOSAnalogInverter': 'Inverter',
	'MosfetCascodedNMOSAnalogInverter': 'Inverter',
	'MosfetCascodedAnalogInverter': 'Inverter',
	'MosfetCascodeAnalogInverterPmosDiodeTransistor': 'Inverter',
	'MosfetCascodeAnalogInverterNmosDiodeTransistor': 'Inverter',
	'MosfetCascodeNMOSAnalogInverterOneDiodeTransistor': 'Inverter',
	"MosfetCascodePMOSAnalogInverterOneDiodeTransistor": "Inverter",
	"MosfetCascodePMOSAnalogInverterCurrentMirrorLoad": "Inverter",
	"MosfetCascodeNMOSAnalogInverterCurrentMirrorLoad": "Inverter",
	"MosfetCascodeAnalogInverterTwoCurrentMirrorLoads": "Inverter",
	'MosfetAnalogInverter': 'Inverter',
	'MosfetDifferentialPair': 'DiffPair',
	'MosfetFoldedCascodeDifferentialPair': 'DiffPair',
	"MosfetCascodedDifferentialPair": "DiffPair",
	'MosfetSimpleCurrentMirror': 'CM',
	'MosfetImprovedWilsonCurrentMirror': 'CM',
	"MosfetCascodeAnalogInverterPmosCurrentMirrorLoad": "CM",
	"MosfetCascodeAnalogInverterNmosCurrentMirrorLoad": "CM",
	"MosfetFourTransistorCurrentMirror": "CM",
	"MosfetCascodeCurrentMirror": "CM",
	"MosfetWilsonCurrentMirror": "CM",
	"MosfetWideSwingCascodeCurrentMirror": "CM",
	"InverterPmosCurrentMirrorLoad": "CM",
	'CapacitorArray': 'cap',
	'MosfetDiodeArray': 'MosfetDiode',
	'MosfetNormalArray': 'Mosfet'
}
rename_map = {k: 0 for k, _ in rename_map.items()}

def check_add(list_subcircuits):
    """Check if any of the subcircuits in could be used as demonstration circuits.

    :param list_subcircuits: _description_
    :return: _description_
    """
    should_add = False
    global rename_map
    for sc in list_subcircuits:
        if sc in rename_map and rename_map[sc] == 0:
            rename_map[sc] = 1
            should_add = True
    return should_add

def get_demonstration_examples():
    all_examples = []
    for dir in ["small", "medium"]:
        for i in range(1, 101):
            netlist_dir = f"data/benchmark-asi-100-train/{dir}/{i}/"
            tree = ET.parse(glob.glob(os.path.join(netlist_dir, "structure_result.xml"))[0])
            root = tree.getroot()
            subcircuits = root[1]

            all_subcircuits = []
            for sc in subcircuits:
                circuit_name = sc.attrib['name']
                circuit_name = circuit_name[:circuit_name.find("[")]
                all_subcircuits.append(circuit_name)
            
            if check_add(all_subcircuits):
                all_examples.append(netlist_dir)
    
    print ("all_examples:", all_examples) 
    print ("length all_examples:", len(all_examples))
    return all_examples

def check_cover(examples):
    flag_indicator = {
        'MosfetCascodedPMOSAnalogInverter': 'Inverter',
        'MosfetCascodedNMOSAnalogInverter': 'Inverter',
        'MosfetCascodedAnalogInverter': 'Inverter',
        'MosfetCascodeAnalogInverterPmosDiodeTransistor': 'Inverter',
        'MosfetCascodeAnalogInverterNmosDiodeTransistor': 'Inverter',
        'MosfetCascodeNMOSAnalogInverterOneDiodeTransistor': 'Inverter',
        "MosfetCascodePMOSAnalogInverterOneDiodeTransistor": "Inverter",
        "MosfetCascodePMOSAnalogInverterCurrentMirrorLoad": "Inverter",
        "MosfetCascodeNMOSAnalogInverterCurrentMirrorLoad": "Inverter",
        "MosfetCascodeAnalogInverterTwoCurrentMirrorLoads": "Inverter",
        'MosfetAnalogInverter': 'Inverter',
        'MosfetDifferentialPair': 'DiffPair',
        'MosfetFoldedCascodeDifferentialPair': 'DiffPair',
        "MosfetCascodedDifferentialPair": "DiffPair",
        'MosfetSimpleCurrentMirror': 'CM',
        'MosfetImprovedWilsonCurrentMirror': 'CM',
        "MosfetCascodeAnalogInverterPmosCurrentMirrorLoad": "CM",
        "MosfetCascodeAnalogInverterNmosCurrentMirrorLoad": "CM",
        "MosfetFourTransistorCurrentMirror": "CM",
        "MosfetCascodeCurrentMirror": "CM",
        "MosfetWilsonCurrentMirror": "CM",
        "MosfetWideSwingCascodeCurrentMirror": "CM",
        "InverterPmosCurrentMirrorLoad": "CM",
        'CapacitorArray': 'cap',
        'MosfetDiodeArray': 'MosfetDiode',
        'MosfetNormalArray': 'Mosfet'
    }
    flag_indicator = {k: 0 for k, _ in flag_indicator.items()}




    for ex in examples:
        tree = ET.parse(glob.glob(os.path.join(ex, "structure_result.xml"))[0])
        root = tree.getroot()
        subcircuits = root[1]

        all_subcircuits = []
        for sc in subcircuits:
            circuit_name = sc.attrib['name']
            circuit_name = circuit_name[:circuit_name.find("[")]
            all_subcircuits.append(circuit_name)

            flag_indicator[circuit_name] = 1
    
    return 0 not in flag_indicator.values()
        


def create_gen_rule_prompt():
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

Let's think step by step.
    """)
    return prompt

def create_update_rule_prompt():
    prompt = PromptTemplate.from_template(
    """
You are improving a set of identification instructions and rules for recognizing analog subcircuits (e.g., Differential Pair, Current Mirror, Inverter) in flat SPICE netlists.

Below, for each example, you are given:

- A flat SPICE netlist.
- The subcircuits predicted using the current identification rules.
- The ground-truth subcircuits.
- Evaluation metrics (precision, recall, F1 score) for each subcircuit type.

Your task is to:

- Analyze the discrepancies between predicted and ground-truth subcircuits.
- Identify likely causes of false positives and false negatives.
- Propose an improved version of the identification rules that addresses the observed issues.

Output only the revised instructions and rules in Markdown format (no commentary), structured step-by-step and clearly separated by subcircuit type.

Original Identification Rules:
```
{instruction}
```

Evaluation Logs:
```
{eval_log}
```
\n

Task:

Use the above feedback to revise the identification rules to reduce false positives while maintaining correct matches. The revised rules should be:

- Written in Markdown
- Structured step-by-step
- Divided by subcircuit type (e.g., Differential Pair, Current Mirror)
- Ready for use in identifying new subcircuits

Let's think step by step

    """)
    return prompt

def create_examples(demonstration_examples):
    examples = ""
    for i, netlist in enumerate(demonstration_examples):
        data = SPICENetlist(netlist)

        examples += f"\nExample {i}: \nSPICE Netlist:\n\n```\n{data.netlist}```\nGround Truth: {data.hl2_gt}"
        examples += "\n------------------------------"
    return examples




def gen_inital_rules(save_path="data/gen_rules/gen_rules_0_deepseek.md", examples=None):
    # model = deepseek()
    model = load_ollama("llama3:70b")
    chain = create_gen_rule_prompt() | model
    output = chain.invoke({'examples': create_examples(examples)})
    print (output.content)

    Path("data/gen_rules").mkdir(parents=True, exist_ok=True)   
    with open(save_path, "w") as f:
        f.write(output.content)

def show_generated_prompt(examples=None):
    output =  create_gen_rule_prompt().invoke({'examples':  create_examples(examples)}).to_string()
    print (output)


def create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided(instruction):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify the following functional building blocks: Differential Pair (DiffPair), Current Mirror (CM), and Simple or Cascoded Analog Inverter (Inverter).\n" +
                f"When answering the question, use the provided definition, connection rules, and procedure to identify these functional building blocks. " +
                "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n" +
                "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)\n" +
                "- 'transistor_names': a list of transistor names that belong to this building block\n" +
                "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n\n" + 
                f"Instructions:\n {instruction}"
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt


    
def eval_rule(kb, demonstration_examples):
    model = load_ollama("llama3:70b")
    results = []
    logs = []
    # with open(f"data/gen_rules/gen_rules_0_deepseek.md", "r") as f:
    #     kb = f.read()

    print (".......")
    print (len(demonstration_examples))
    for ex in demonstration_examples:
        data = SPICENetlist(ex)
        prompt = create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided(kb)
        output, parsed_data = llm_invoke(model, prompt, data)
        eval_results = compute_cluster_metrics(predicted=parsed_data, ground_truth=data.hl2_gt)
        results.append(eval_results)
        logs.append({"netlist": data.netlist, "predicted": parsed_data, "ground_truth": data.hl2_gt, "eval_results": eval_results})

    
    metrics = average_metrics(results)
    return metrics, logs


if __name__ == "__main__":
    demonstration_examples =  get_demonstration_examples()

    name = "llama3.70b-rules"
    model_id = "llama3:70b"
    for step in range(5):

        if step == 0:
            rule_fn = f"data/gen_rules/{name}-0-out.md"
            gen_inital_rules(rule_fn, demonstration_examples)
            # show_generated_prompt(demonstration_examples)
            
            with open(rule_fn, "r") as f:
                instruction = f.read()
        else:
            rule_fn = f"data/gen_rules/{name}-{step-1}-out.md"

            with open(rule_fn, "r") as f:
                instruction = f.read()

        metrics, logs = eval_rule(instruction, demonstration_examples)
        print (metrics)
        eval_log  = ""
        for i in range(len(logs)):
            print ("\nExample {i}: \n")
            print ("ground_truth: ", logs[i]["ground_truth"])
            print ("predicted: ", logs[i]["predicted"])
            print ("eval_results: ", logs[i]["eval_results"])
            print ("\n------------------------------\n")

            data = SPICENetlist(demonstration_examples[i])
            eval_log += f"\nExample {i}: \n"
            eval_log += f"{data.netlist}"
            eval_log += "ground_truth: " + str(logs[i]["ground_truth"]) + "\n"
            eval_log += "predicted: " + str(logs[i]["predicted"]) + "\n"
            eval_log += "eval_results: "+ str(logs[i]["eval_results"])
            eval_log += "\n------------------------------"
        
        prompt = create_update_rule_prompt().invoke({'instruction': instruction, 'eval_log': eval_log}).to_string()
        print (prompt) 

        model = load_ollama(model_id)
        chain = create_update_rule_prompt() | model
        output = chain.invoke({'instruction': instruction, 'eval_log': eval_log})
        print (output.content)
        with open(f"data/gen_rules/{name}-{step}-out.md", "w") as f:
            f.write(output.content)


        with open(f"data/gen_rules/{name}-{step}-info.md", "w") as f:
            f.write("\ncurrent metrics: " + str(metrics))
            f.write("\n--------------------------------\n")
            f.write(prompt)
            f.write("\n--------------------------------\n")
            f.write("\n\n" + eval_log)
