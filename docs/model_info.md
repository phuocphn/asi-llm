## DeepSeek-V3

| Model Name | Size |
| --- | --- |
| DeepSeek-V2|    236 billion parameters|
| DeepSeek-V2.5|  236 billion parameters|
| DeepSeek-V3|    671 billion parameters|
| DeepSeek-R1|    671 billion parameters|
| DeepSeek-Coder| 1B, 5.7B, 6.7B, and 33B parameters|
|  DeepSeek-VL2|   1.0B, 2.8B, and 4.5B activated parameters|


Q: What is the `deepseek-r1:70b` in this case ?
```
def test_ollma_model():
    model_id = "deepseek-r1:70b"
    model =  ChatOllama(model=model_id, 
                temperature = 0.0,
                max_tokens = 15000, 
                device=0,
                num_ctx=512,
            )
    response = model.invoke("Hi!")
    print(response.content)
```

A: DeepSeek-R1:70B is a 70-billion parameter, **"distilled"** language model based on the Llama-3.3-70B-Instruct model, designed for reasoning tasks, and offers a balance of accuracy and efficiency (it is not the "real" r1). [[reddit](https://www.reddit.com/r/LocalLLaMA/comments/1ic0v57/what_model_is_deepseekr1_online/#:~:text=There's%206%20distillations%20and%20the,%E2%80%A2%202mo%20ago)]

- The ollama 671B model is the "real R1" but at a q4_m_k GGUF quantization (4 bits per parameter instead of the full 16 bits per parameter) which makes it take about 1/4th the required RAM as the full FP16 version of the model. Slightly less quality than the full version, but still the "real" MoE architecture [[reddit](https://www.reddit.com/r/LocalLLaMA/comments/1ic0v57/what_model_is_deepseekr1_online/#:~:text=There's%206%20distillations%20and%20the,%E2%80%A2%202mo%20ago)].

- [[deepseek-v2.5 / ollama](https://ollama.com/library/deepseek-v2.5)]
- [[deepseek-v2 / ollama](https://ollama.com/library/deepseek-v2:236b)]


### Models used in Literature
- claude-3-haiku-20240307 [[youtube](https://www.youtube.com/watch?v=HtiCbeYzlJk)]
