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
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract diode-connected transistors." + 
                "Provide your answer in JSON format." + "\n" + 
                "The output should be a list of dictionaries. Each dictionary must have two keys: " + "\n" +
                "- 'sub_circuit_name': with the value of `MosfetDiode`" + "\n" + 
                "- 'transistor_names': a list of transistor names that belong to this building block" + "\n" +
                "Wrap your response between <json> and </json> tags." + "\n" 
            ),
            ("human", "Input SPICE netlist\n{netlist} \nLet's think step-by-step."),
        ]
    )#.partial(format_instructions=parser.get_format_instructions())
    return prompt


def create_prompt_hl2():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design." +  
                "Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), Simple and Cascoded Analog Inverter (Inverter)" + "\n" + 
                "Provide your output in JSON format, " + 
                "as a list of dictionaries. Each dictionary must contain two keys: " + "\n" +
                "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)" + "\n" +
                "- 'transistor_names': a list of transistor names that belong to this building block" + "\n" +
                "Wrap your response between <json> and </json> tags. Do not output any further explanation, description, or comments." + "\n" 
            ),
            ("human", "Input SPICE netlist\n{netlist} \nLet's think step-by-step."),
        ]
    )
    return prompt


def create_prompt_hl2_with_target_single_subcircuit_only(subcircuit_name = "Current Mirror", abbreviation = "CM"):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract available {subcircuit_name} ({abbreviation})." +  
                "Provide your output in JSON format, " + 
                "as a list of dictionaries. Each dictionary must contain two keys: " + "\n" +
                f"- 'sub_circuit_name': '{abbreviation}' " + "\n" +
                f"- 'transistor_names': a list of transistor names that belong to this {subcircuit_name}" + "\n" +
                "Wrap your response between <json> and </json> tags. Do not output any further explanation, description, or comments." + "\n" 
            ),
            ("human", "Input SPICE netlist\n{netlist} \nLet's think step-by-step."),
        ]
    )
    return prompt

def create_prompt_hl2_with_target_single_subcircuit_only_and_fixed_rule_provided(subcircuit_name = "Current Mirror", abbreviation = "CM"):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract available {subcircuit_name} ({abbreviation})." +  
                f"When you answer the questions, try to use the provided definition, connection rules, identification procedure to identify {subcircuit_name}." + 
                "Provide your output in JSON format, " + 
                "as a list of dictionaries. Each dictionary must contain two keys: " + "\n" +
                f"- 'sub_circuit_name': '{abbreviation}' " + "\n" +
                f"- 'transistor_names': a list of transistor names that belong to this {subcircuit_name}" + "\n" +
                "Wrap your response between <json> and </json> tags. Do not output any further explanation, description, or comments." + "\n" 

                f"Knowledge Base: \n {get_knowledge_base()[abbreviation]}" +  "\n" 
            ),
            ("human", "Input SPICE netlist\n{netlist} \nLet's think step-by-step."),
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
        assert isinstance(parsed_data, list), "parsed data is not a list"
        return output, parsed_data
    except json.decoder.JSONDecodeError as e:
        logger.error (f"parsing LLM output failed")
        return None, None

    except Exception as e:
        logger.error (f"exception: {e}")
        return None, None

def identify_devices(subset="medium", model=None, prompt=None, category="single"):
    results = []
    i = 1
    max_i  = 101

    num_attempts = 0
    max_attempts = 5

    while i <  max_i and num_attempts < max_attempts:
        data = SPICENetlist(f"data/benchmark-asi-100/{subset}/{i}/")
        logger.info ("netlist #" + str(i))

        try:
            if len(prompt) == 1:
                output, parsed_data = llm_invoke(model, prompt[0], data)
                parsed_data = parsed_data
            else:
                parsed_data = []
                output = []
                for p in prompt:
                    partial_output, partial_parsed_data = llm_invoke(model, p, data)
                    if output is not None and partial_parsed_data is not None:
                        parsed_data += partial_parsed_data
                        output.append(partial_output.content)
                output = "\n".join(output)
        except Exception as e:
            logger.error (f"exception: {e}")
            num_attempts += 1
            continue
                

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

        i += 1
    #return average_metrics(results)
    return results


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config : DictConfig) -> None:

    logger.info (OmegaConf.to_yaml(config) + "\n\n\n")

    if config.eval_llms == "small":
        llm_models = config.small_llms
    elif config.eval_llms == "medium":
        llm_models = config.medium_llms
    elif config.eval_llms == "all":
        llm_models = config.all_llms


    input("Press Enter to continue...")

    # get current time as a string for file name
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    for subset in config.benchmark_subsets:
        for model_id in llm_models:
            llm =load_ollama(model_id)
            for category in config.categories: #["single", "pair"]:
                if category == "single":
                    prompt = create_prompt_hl1()
                    result = average_metrics(identify_devices(subset, llm, prompt=[prompt], category=category))

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

                        result = average_metrics(identify_devices(subset, llm, prompt=prompts, category=category))
                    else:
                        prompt = create_prompt_hl2()
                        result = average_metrics(identify_devices(subset, llm, prompt=[prompt], category=category))

                logger.info (f"**result**: model={model_id},category={category}:   {result}")

                # write result to file
                with open(f"results/{now}.txt", "a") as fw:
                    fw.write(f"model={model_id},subset={subset},category={category}:   {result}\n")

if __name__ == "__main__":
    main()