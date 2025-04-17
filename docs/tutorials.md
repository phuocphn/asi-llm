# Langchain 

**Structured Output**

1. Serialization - [[Pydantic](https://docs.pydantic.dev/latest/concepts/serialization/#advanced-include-and-exclude)] 
2. ChatOllama and .with_structured_output() Implement .with_structured_output() for Ollama models · langchain-ai/langchain · Discussion #27497 [[#github](https://github.com/langchain-ai/langchain/discussions/27497)]
3. How To Use Meta Llama3 With Huggingface And Ollama - [[#youtube](https://www.youtube.com/watch?v=LA-hZDnn5Hc)]

```
from langchain_ollama import ChatOllama
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

model = ChatOllma(model="llama3.1").with_structured_output(Person)
model.invoke("Erick 27")
```



**Use Ollama with Langchain/Python**
1. langchain/docs/docs/integrations/chat/ollama.ipynb at master · [[langchain-ai/langchain ](https://github.com/langchain-ai/langchain/blob/master/docs/docs/integrations/chat/ollama.ipynb)]

```
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)
```

2. Prompt Templates [[langchain](https://python.langchain.com/docs/concepts/prompt_templates/)]

It is possible to utilize existing ChatOpenAI wrapper from Langchain to deploy other LLMs [[stackoverfolow](https://stackoverflow.com/questions/77520963/using-locally-deployed-llm-with-langchains-openai-llm-wrapper)] [[github](https://github.com/langchain-ai/langchain/discussions/8896)]

```
from langchain_community.chat_models import ChatOpenAI

llm = ChatOpenAI(
        openai_api_base="http://<host-ip>:<port>/<v1>",
        openai_api_key="dummy_value",
        model_name="model_deployed")
```


`ChatOpenAI` is intended to support the OpenAI API. Try using `BaseChatOpenAI`, which accommodates many APIs that are similar to OpenAI. It uses tool calling for structured output by default.

```
from langchain_openai.chat_models.base import BaseChatOpenAI

llm = BaseChatOpenAI()
```

Deepseek [[sample call](https://cdn.deepseek.com/api-docs/deepseek_langchain.py)]

- How to Make LLMs More Reliable with `field_validator` [[youtube](https://www.youtube.com/watch?v=HtiCbeYzlJk)] [[code](https://github.com/JohannesJolkkonen/llm-self-critique/blob/main/app.ipynb)]


