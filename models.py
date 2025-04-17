import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI


def load_ollama(model_name="deepseek-r1:70b"):
    return ChatOllama(model=model_name, temperature=0.0, max_tokens=4096, device=0)


def load_openai(model_name="gpt-4o"):
    openai_api_key = os.getenv("OPENAI_API_KEY", None)
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    return ChatOpenAI(
        model=model_name,
        temperature=0,
        max_tokens=4096,
        timeout=None,
        max_retries=2,
        api_key=openai_api_key,
    )


def load_deepseek(model_name="deepseek-reasoner"):
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", None)
    if deepseek_api_key is None:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

    model = BaseChatOpenAI(
        model=model_name,
        openai_api_key=deepseek_api_key,
        openai_api_base="https://api.deepseek.com",
        max_tokens=4096,
    )
    return model
