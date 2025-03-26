import transformers
import torch
import os

from calc_accuracy import evaluate_prediction, average_metrics
from pydantic import BaseModel, Field
from netlist_collection import get_netlist, get_groundtruth
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import  ChatOllama
from langchain_openai import ChatOpenAI


def load_ollama():
    model_id = "llama3:70b"
    model_id = "deepseek-r1:70b"
    model_id = "llama3:70b-instruct"
    model_id = "llama3.3:70b"

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


class AnswerFormat(BaseModel):
    reasoning_steps: list[str] = Field(description="The reasoning steps leading to the final conclusion") 
    number_of_diode_connected_transistors: int = Field(description="The number of diode-connected transistors")
    transistor_names: list[str] = Field(description="The names of the diode-connected transistors")

metrics_list = []
for i in range(1, 11):
    print ("netlist #" + str(i))
    query =  f"""Please act as an experienced analog designer. Given an INPUT SPICE NETLIST, your task is to identify all diode-connected transistors.

    INPUT SPICE NETLIST:
    {get_netlist(i)}

    Let's think step-by-step.
    """
    try:
        # structured_llm = llm.with_structured_output(AnswerFormat)
        # output_1 = structured_llm.invoke(query)

        # another way to do it
        parser = PydanticOutputParser(pydantic_object=AnswerFormat)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Answer the user query. Wrap the output in `json` tags\n{format_instructions}",
                ),
                ("human", "{query}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())
        print(prompt.invoke(query).to_string())

        chain = prompt | llm | parser
        output = chain.invoke({"query": query})

    except Exception as e:
        output = llm.invoke(query)
        print (output)
        continue

    # print (output.model_dump_json(indent=2))

    print ("------------------------------------")
    print ("ground truth: ", get_groundtruth(i))
    precision = evaluate_prediction(output.model_dump(), get_groundtruth(i))
    print (f"{precision=}")
    print ("------------------------------------")
    metrics_list.append(precision)

print (average_metrics(metrics_list))