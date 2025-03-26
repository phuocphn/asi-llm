**Structured Output**

1. Serialization - Pydantic https://docs.pydantic.dev/latest/concepts/serialization/#advanced-include-and-exclude
2. ChatOllama and .with_structured_output() Implement .with_structured_output() for Ollama models · langchain-ai/langchain · Discussion #27497 https://github.com/langchain-ai/langchain/discussions/27497
3. How To Use Meta Llama3 With Huggingface And Ollama - YouTube https://www.youtube.com/watch?v=LA-hZDnn5Hc

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
1. langchain/docs/docs/integrations/chat/ollama.ipynb at master · langchain-ai/langchain https://github.com/langchain-ai/langchain/blob/master/docs/docs/integrations/chat/ollama.ipynb

```
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)
```

2. 