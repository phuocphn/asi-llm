from models import load_llms

model = load_llms("grok-3-beta")
print(model.invoke("What is the captial of France?"))
