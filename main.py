from pathlib import Path
import transformers
import torch
import os
import json

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import  ChatOllama
from langchain_openai import ChatOpenAI

from calc1 import compute_cluster_metrics, compute_cluster_metrics_hl1, average_metrics
from src.netlist import SPICENetlist
from src.kb import get_knowledge_base
import hydra
from omegaconf import DictConfig, OmegaConf


#-----
from loguru import logger
import sys
import datetime
log_level = "DEBUG"
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logfile = f"logs/{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.txt"
logger.remove() #Why does it logs duplicated message? · Issue #208 · Delgan/loguru https://github.com/Delgan/loguru/issues/208
logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
logger.add(logfile, level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)


class AnswerFormat(BaseModel):
    reasoning_steps: list[str] = Field(description="The reasoning steps leading to the final conclusion") 
    number_of_diode_connected_transistors: int = Field(description="The number of diode-connected transistors")
    transistor_names: list[str] = Field(description="The names of the diode-connected transistors")


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

def create_prompt_hl1():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract diode-connected transistors (MosfetDiode), load capacitors (load_cap), and compensation capacitors (compensation_cap). " +
                "Provide your answer in JSON format.\n" +
                "The output should be a list of dictionaries. Each dictionary must have two keys:\n" +
                "- 'sub_circuit_name': the type of device, corresponding to one of the acronyms (MosfetDiode, load_cap, or compensation_cap)\n" +
                "- 'transistor_names': a list of transistor names that belong to this building block\n" +
                "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n"
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step.")
        ]
    )
    return prompt


def create_prompt_hl2():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. " +
                "Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), and Simple or Cascoded Analog Inverter (Inverter).\n" +
                "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n" +
                "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)\n" +
                "- 'transistor_names': a list of transistor names that belong to this building block\n" +
                "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n"
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt


def create_prompt_hl2_with_target_single_subcircuit_only(subcircuit_name = "Current Mirror", abbreviation = "CM"):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name} ({abbreviation}). " +
                "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n" +
                f"- 'sub_circuit_name': '{abbreviation}'\n" +
                f"- 'transistor_names': a list of transistor names that belong to this {subcircuit_name}\n" +
                "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n"
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt

def create_prompt_hl2_with_target_single_subcircuit_only_and_fixed_rule_provided(subcircuit_name = "Current Mirror", abbreviation = "CM"):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract all available {subcircuit_name}s ({abbreviation}). " +
                f"When answering the question, use the provided definition, connection rules, and identification procedure to identify {subcircuit_name}s. " +
                "Provide your output in JSON format as a list of dictionaries. Each dictionary must contain two keys:\n" +
                f"- 'sub_circuit_name': '{abbreviation}'\n" +
                f"- 'transistor_names': a list of transistor names that belong to this {subcircuit_name}\n" +
                "Wrap your response between <json> and </json> tags. Do not include any explanation, description, or comments.\n\n" +
                f"Knowledge Base:\n{get_knowledge_base()[abbreviation]}\n"
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt

def create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided(config):
    if config.rule_src is None:
        knowedge_base = f"{get_knowledge_base()['DiffPair']}\n {get_knowledge_base()['CM']} \n {get_knowledge_base()['Inverter']}"
    else:
        with open(config.rule_src, "r") as f:
            knowedge_base = f.read()
        
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
                f"Knowledge Base:\n ```\n{knowedge_base}\n```\n"
            ),
            ("human", "Input SPICE netlist:\n{netlist}\nLet's think step by step."),
        ]
    )
    return prompt

def llm_invoke(model, prompt, data):
    try:
        # prompt = create_prompt_hl2()
        logger.info(prompt.invoke(data.netlist).to_string())
        chain = prompt | model #| parser
        output = chain.invoke({"netlist": data.netlist})
        parsed_data = json.loads(output.content[output.content.find("<json>") + len("<json>"):output.content.find("</json>")])
        assert isinstance(parsed_data, list), "parsed data is not a list: " + str(parsed_data)
        return output, parsed_data
    except json.decoder.JSONDecodeError as e:
        logger.error (f"parsing LLM output failed: " + output.content)
        return None, None

    except Exception as e:
        logger.error (f"exception: {e}")
        return None, None

def format_cluster_info(results):
    out = ""
    for res in results:
        out += str(res) + "\n"
    return out


def identify_devices(subset="medium", model=None, prompts=None, category="single", metadata=None):
    results = []
    i = 1
    max_i  = 101

    num_attempts = 0
    max_attempts = 5

    while i <  max_i and num_attempts < max_attempts:
        data = SPICENetlist(f"data/benchmark-asi-100/{subset}/{i}/")
        logger.info ("netlist #" + str(i))

        try:
            if len(prompts) == 1:
                outputs = []
                output, parsed_data = llm_invoke(model, prompts[0], data)
                parsed_data = parsed_data
                if output is  None or parsed_data is  None:
                    raise Exception("LLM output is None")
                outputs.append(output.content)
            else:
                parsed_data = []
                outputs = []
                for p in prompts:
                    partial_output, partial_parsed_data = llm_invoke(model, p, data)
                    if output is not None and partial_parsed_data is not None:
                        parsed_data += partial_parsed_data
                        outputs.append(partial_output.content)
        except Exception as e:
            logger.error (f"exception: {e}")
            num_attempts += 1
            continue
                
        output = "\n".join(outputs)
        logger.info (f"# output={output}")

    
        logger.info ("------------------------------------")
        logger.info (f"predicted_output: {json.dumps(parsed_data, indent=2)}")

        if category == "single":
            logger.info (f"ground truth: {json.dumps(data.hl1_gt, indent=2)}")
            eval_results = compute_cluster_metrics_hl1(predicted=parsed_data, ground_truth=data.hl1_gt)
        elif category == "pair":
            logger.info (f"ground truth: {json.dumps(data.hl2_gt, indent=2)}")
            eval_results = compute_cluster_metrics(predicted=parsed_data, ground_truth=data.hl2_gt)
        else:
            logger.error (f"unknown category: {category}")
            return

        logger.info (f"{eval_results=}")
        logger.info ("------------------------------------")
        results.append(eval_results)

        num_attempts = 0


        # Save prompt and netlist data
        Path(f"{metadata['prediction_dir']}/netlist_{i}").mkdir(parents=True, exist_ok=True)
        with open(f"{metadata['prediction_dir']}/netlist_{i}/data.txt", "w") as fw:
            fw.write(data.netlist)
            fw.write("\n------------------------\n")
            fw.write("hl1_gt: \n" + format_cluster_info(data.hl1_gt))
            fw.write("\n\n")
            fw.write("hl2_gt: \n" + format_cluster_info(data.hl2_gt))
        
        with open(f"{metadata['prediction_dir']}/netlist_{i}/gt_hl1.json", "w") as fw:
            fw.write(json.dumps(data.hl1_gt, indent=2))
        with open(f"{metadata['prediction_dir']}/netlist_{i}/gt_hl2.json", "w") as fw:
            fw.write(json.dumps(data.hl2_gt, indent=2))

        for prompt_index, prompt in enumerate(prompts):
            with open(f"{metadata['prediction_dir']}/netlist_{i}/prompt_{prompt_index}.txt", "w") as fw:
                fw.write(prompt.invoke(data.netlist).to_string())


        # Save the output to a file
        for output_index, output_data in enumerate(outputs):
            with open(f"{metadata['prediction_dir']}/netlist_{i}/output_{output_index}.txt", "w") as fw:
                fw.write(output_data)
                fw.write("\n------------------------\n")

        with open(f"{metadata['prediction_dir']}/netlist_{i}/parsed_data.json", "w") as fw:
            fw.write(json.dumps(parsed_data, indent=2))

        with open(f"{metadata['prediction_dir']}/netlist_{i}/eval_results.json", "w") as fw:
            fw.write(json.dumps(eval_results, indent=2))


        i += 1
    #return average_metrics(results)
    if num_attempts < max_attempts:
        return results
    else:
        return [{"Precision": 0, "Recall": 0, "F1-score": 0}]


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config : DictConfig) -> None:

    logger.info (OmegaConf.to_yaml(config) + "\n\n\n")

    if config.eval_llms == "small":
        llm_models = config.small_llms
    elif config.eval_llms == "medium":
        llm_models = config.medium_llms
    elif config.eval_llms == "all":
        llm_models = config.all_llms


    # input("Press Enter to continue...")

    # get current time as a string for file name
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # create directory if it doesn't exist
    if not os.path.exists(f"outputs/predictions/{now}"):
        os.makedirs(f"outputs/predictions/{now}")

    for subset in config.benchmark_subsets:
        for model_id in llm_models:
            llm =load_ollama(model_id)
            for category in config.categories: #["single", "pair"]:
                prediction_dir = f"outputs/predictions/{now}/subset_{subset}_{model_id}_{category}"
                metadata = {'subset': subset, 'model_id': model_id, 'category': category, 'prediction_dir': prediction_dir}

                if not os.path.exists(prediction_dir):
                    os.makedirs(prediction_dir)

                if category == "single":
                    prompt = create_prompt_hl1()
                    result = average_metrics(identify_devices(subset, llm, prompts=[prompt], category=category, metadata=metadata))

                elif category == "pair":
                    if config.break_hl2_prompt:
                        prompts = []
                        for subcircuit_name, abbreviation in config.subcircuits.items():
                            if config.rule_provided:
                                prompt = create_prompt_hl2_with_target_single_subcircuit_only_and_fixed_rule_provided(subcircuit_name=subcircuit_name, abbreviation=abbreviation)
                                prompts.append(prompt)
                            else:
                                prompt = create_prompt_hl2_with_target_single_subcircuit_only(subcircuit_name=subcircuit_name, abbreviation=abbreviation)
                                prompts.append(prompt)

                        result = average_metrics(identify_devices(subset, llm, prompts=prompts, category=category,  metadata=metadata))
                    else:
                        if config.rule_provided:
                            prompt = create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided(config)
                            result = average_metrics(identify_devices(subset, llm, prompts=[prompt], category=category, metadata=metadata))

                        else:
                            prompt = create_prompt_hl2()
                            result = average_metrics(identify_devices(subset, llm, prompts=[prompt], category=category, metadata=metadata))

                logger.info (f"**result**: model={model_id},category={category}:   {result}")

                # write result to file
                with open(f"results/{now}.txt", "a") as fw:
                    fw.write(f"model={model_id},subset={subset},category={category}:   {result}\n")

if __name__ == "__main__":
    main()