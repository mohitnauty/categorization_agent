from groq import Groq
import os

from services.sensitive_data_guard import redact_text


class GroqClient:

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, prompt):
        safe_prompt = redact_text(prompt)

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": safe_prompt}],
            model="llama3-8b-8192"
        )

        return response.choices[0].message.content
