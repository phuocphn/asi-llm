# gemini-2.5-pro-exp-03-25
# gemini-2.0-flash
import os
from google import genai


class google_genai_model:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_AI_KEY", None)
        self.client = genai.Client(api_key=google_api_key)

    def invoke(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-pro-exp-03-25", contents=prompt
        )
        return response.text


model = google_genai_model()
print(model.invoke("What is the capital of China?"))
