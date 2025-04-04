import transformers
import torch
import os
import json

from calc_accuracy import evaluate_prediction, average_metrics, average_metrics_v2
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import  ChatOllama
from langchain_openai import ChatOpenAI

from calc1 import compute_cluster_metrics, compute_cluster_metrics_hl1
from netlist import SPICENetlist

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


def create_prompt_hl2_current_mirrors_only():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract available current mirrors (CM)." +  
                "Provide your output in JSON format, " + 
                "as a list of dictionaries. Each dictionary must contain two keys: " + "\n" +
                "- 'sub_circuit_name': 'CM' " + "\n" +
                "- 'transistor_names': a list of transistor names that belong to this current mirror" + "\n" +
                "Wrap your response between <json> and </json> tags. Do not output any further explanation, description, or comments." + "\n" 
            ),
            ("human", "Input SPICE netlist\n{netlist} \nLet's think step-by-step."),
        ]
    )
    return prompt

def identify_devices(subset="medium", model=None, prompt=None, category="single"):
    results = []
    i = 1
    max_i  = 11

    num_attempts = 0
    max_attempts = 30

    while i <  max_i and num_attempts < max_attempts:
        data = SPICENetlist(f"data/{subset}/netlist{i}/")
        logger.info ("netlist #" + str(i))
        try:
            # prompt = create_prompt_hl2()
            logger.info(prompt.invoke(data.netlist).to_string())
            chain = prompt | model #| parser
            output = chain.invoke({"netlist": data.netlist})

        except Exception as e:
            logger.error (f"exception: {e}")
            return
        
        logger.info (f"# output={output}")

        try:
            predicted_output = json.loads(output.content[output.content.find("<json>") + len("<json>"):output.content.find("</json>")])
    
            logger.info ("------------------------------------")
            logger.info (f"predicted_output: {json.dumps(predicted_output, indent=2)}")

            if category == "single":
                logger.info (f"ground truth: {json.dumps(data.hl1_gt, indent=2)}")
                eval_results = compute_cluster_metrics_hl1(predicted=predicted_output, ground_truth=data.hl1_gt)
            elif category == "pair":
                logger.info (f"ground truth: {json.dumps(data.hl2_gt, indent=2)}")
                eval_results = compute_cluster_metrics(predicted=predicted_output, ground_truth=data.hl2_gt)
            else:
                logger.error (f"unknown category: {category}")
                return

            logger.info (f"{eval_results=}")
            logger.info ("------------------------------------")
            results.append(eval_results)

            num_attempts = 0
        except json.decoder.JSONDecodeError as e:
            logger.error (f"parsing LLM output failed, retry {num_attempts}...")
            num_attempts += 1
            continue
        except Exception as e:
            logger.exception (f"exception: {e}")
            logger.error (f"could not compute comparison metrics, retry {num_attempts}...")
            num_attempts += 1
            continue

        i += 1
    return average_metrics_v2(results)

logger.info ("\n\n\n")

llm_models = [
    "deepseek-r1:70b",
    "llama3.3:70b",
    "llama3:70b",
    "llama3:70b-instruct",
    "mistral:7b-instruct",
    "mixtral:8x22b"
]
llm_models = [
    "mistral:7b-instruct",
]
llm_models = [
    "deepseek-r1:70b",
]

subset = "medium" # "small", "medium", "large"
for model_id in llm_models:
    llm =load_ollama(model_id)
    for category in ["single", "pair"]:
        if category == "single":
            prompt = create_prompt_hl1()
        elif category == "pair":
            prompt = create_prompt_hl2()

        result = identify_devices(subset, llm, prompt=prompt, category=category)
        logger.info (f"**result**: model={model_id}, category={category}:   {result}")