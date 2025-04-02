import transformers
import torch
import os
import json

from calc_accuracy import evaluate_prediction, average_metrics, average_metrics_v2
from pydantic import BaseModel, Field
from netlist_collection import get_netlist, get_groundtruth
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import  ChatOllama
from langchain_openai import ChatOpenAI

from src.extract_circuit_info import get_hl2_cluster_labels, get_hl1_cluster_labels
from mask_net import get_masked_netlist
from calc1 import compute_cluster_metrics

class SPICENetlist():
    def __init__ (self, netlist_path):
        self.netlist = get_masked_netlist(netlist_path, True)
        self.hl1_gt = get_hl1_cluster_labels(netlist_path)
        self.hl2_gt = get_hl2_cluster_labels(netlist_path)
    
class AnswerFormat(BaseModel):
    reasoning_steps: list[str] = Field(description="The reasoning steps leading to the final conclusion") 
    number_of_diode_connected_transistors: int = Field(description="The number of diode-connected transistors")
    transistor_names: list[str] = Field(description="The names of the diode-connected transistors")


def load_ollama():

    # model_id = "deepseek-r1:70b"
    # model_id = "llama3.3:70b"
    # model_id = "llama3:70b"
    # model_id = "llama3:70b-instruct"
    # model_id = "mistral-large:latest"
    model_id = "mixtral:8x22b"

    print ("use ollama with model id: ", model_id)
    llm = ChatOllama(model=model_id)
    return llm

def loadopenai():
    model_id = "gpt-4o"
    openai_api_key=os.getenv('OPENAI_API_KEY', None)
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    llm = ChatOpenAI(
        model=model_id,
        # temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=openai_api_key,
    )
    print ("use openai with model id: ", model_id)
    return llm

llm =load_ollama()


def identify_HL1_devices():
    results = []
    for i in range(1, 11):
        data = SPICENetlist(f"data/small/netlist{i}/")

        print ("netlist #" + str(i))

        try:
            # parser = PydanticOutputParser(pydantic_object=AnswerFormat)
            # prompt = ChatPromptTemplate.from_messages(
            #     [
            #         (
            #             "system",
            #             "You are an experienced analog circuit designer"
            #             # "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), Simple and Cascoded Analog Inverter (Inverter)" + "\n" + 
            #             # "Provide your answer in JSON format." + "\n" + 
            #             # "The output should be a list of dictionaries. Each dictionary must have two keys: " + "\n" +
            #             # "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)" + "\n" +
            #             # "- 'transistor_names': a list of transistor names that belong to this building block" + "\n" +
            #             # "Wrap your response with <json> and </json> tags." + "\n" 
            #         ),
            #         # ("human", "Input SPICE netlist\n {netlist}"),
            #         # ("Let's think step-by-step")
            #     ]
            # )#.partial(netlist=get_netlist(i))
            # parser = PydanticOutputParser(pydantic_object=AnswerFormat)

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


            print(prompt.invoke(data.netlist).to_string())
            chain = prompt | llm #| parser
            output = chain.invoke({"netlist": data.netlist})

        except Exception as e:
            print ("exception: ", e)
            query =  f"""You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), Simple and Cascoded Analog Inverter (Inverter)
            
            Provide your answer in JSON format.
            The output should be a list of dictionaries. Each dictionary must have two keys:
            - "sub_circuit_name": the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)
            - "transistor_names": a list of transistor names that belong to this building block

            Wrap your response with <json> and </json> tags.

            Input SPICE netlist
            {data.netlist}

            Let's think step-by-step.
            """

            output = llm.invoke(query)
            continue

        # print (output.model_dump_json(indent=2))
        print ("# output=", output)
        returned_json = json.loads(output.content[output.content.find("<json>") + len("<json>"):output.content.find("</json>")])
        print ("predicted:", returned_json)
        print ("ground truth:", data.hl1_gt)
        
        print ("------------------------------------")
        eval_results = compute_cluster_metrics(predicted=returned_json, ground_truth=data.hl1_gt)
        print (eval_results)
        # print ("ground truth: ", get_groundtruth(i))
        # precision = evaluate_prediction(output.model_dump(), get_groundtruth(i))
        # print (f"{precision=}")
        print ("------------------------------------")
        results.append(eval_results)
    
    print (average_metrics_v2(results))

def identify_HL2_devices():
    results = []
    for i in range(1, 11):
        data = SPICENetlist(f"data/medium/netlist{i}/")

        print ("netlist #" + str(i))

        try:
            # parser = PydanticOutputParser(pydantic_object=AnswerFormat)
            # prompt = ChatPromptTemplate.from_messages(
            #     [
            #         (
            #             "system",
            #             "You are an experienced analog circuit designer"
            #             # "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), Simple and Cascoded Analog Inverter (Inverter)" + "\n" + 
            #             # "Provide your answer in JSON format." + "\n" + 
            #             # "The output should be a list of dictionaries. Each dictionary must have two keys: " + "\n" +
            #             # "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)" + "\n" +
            #             # "- 'transistor_names': a list of transistor names that belong to this building block" + "\n" +
            #             # "Wrap your response with <json> and </json> tags." + "\n" 
            #         ),
            #         # ("human", "Input SPICE netlist\n {netlist}"),
            #         # ("Let's think step-by-step")
            #     ]
            # )#.partial(netlist=get_netlist(i))
            # parser = PydanticOutputParser(pydantic_object=AnswerFormat)

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), Simple and Cascoded Analog Inverter (Inverter)" + "\n" + 
                        "Provide your answer in JSON format." + "\n" + 
                        "The output should be a list of dictionaries. Each dictionary must have two keys: " + "\n" +
                        "- 'sub_circuit_name': the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)" + "\n" +
                        "- 'transistor_names': a list of transistor names that belong to this building block" + "\n" +
                        "Wrap your response between <json> and </json> tags." + "\n" 
                    ),
                    ("human", "Input SPICE netlist\n{netlist} \nLet's think step-by-step."),
                ]
            )#.partial(format_instructions=parser.get_format_instructions())


            print(prompt.invoke(data.netlist).to_string())
            chain = prompt | llm #| parser
            output = chain.invoke({"netlist": data.netlist})

        except Exception as e:
            print ("exception: ", e)
            query =  f"""You are an experienced analog circuit designer. Given a SPICE netlist, your task is to identify and extract functional building blocks commonly used in analog design. Specifically, look for the following structures: Differential Pair (DiffPair), Current Mirror (CM), Simple and Cascoded Analog Inverter (Inverter)
            
            Provide your answer in JSON format.
            The output should be a list of dictionaries. Each dictionary must have two keys:
            - "sub_circuit_name": the type of building block, represented using the corresponding acronym (DiffPair, CM, or Inverter)
            - "transistor_names": a list of transistor names that belong to this building block

            Wrap your response with <json> and </json> tags.

            Input SPICE netlist
            {data.netlist}

            Let's think step-by-step.
            """

            output = llm.invoke(query)
            continue

        # print (output.model_dump_json(indent=2))
        print ("# output=", output)
        returned_json = json.loads(output.content[output.content.find("<json>") + len("<json>"):output.content.find("</json>")])
        print ("predicted:", returned_json)
        print ("ground truth:", data.hl2_gt)
        
        print ("------------------------------------")
        eval_results = compute_cluster_metrics(predicted=returned_json, ground_truth=data.hl2_gt)
        print (eval_results)
        # print ("ground truth: ", get_groundtruth(i))
        # precision = evaluate_prediction(output.model_dump(), get_groundtruth(i))
        # print (f"{precision=}")
        print ("------------------------------------")
        results.append(eval_results)
    
    print (average_metrics_v2(results))

identify_HL1_devices()
# identify_HL2_devices()