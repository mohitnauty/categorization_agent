from groq import Groq
import os

from services.sensitive_data_guard import redact_text


class GroqClient:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing in environment")

        self.client = Groq(api_key=api_key)

    def generate(self, prompt):
        safe_prompt = redact_text(prompt)

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": safe_prompt}],
            model="llama-3.1-8b-instant"
        )

        content = response.choices[0].message.content

        # Debug logs (very important for Render)
        print("LLM RESPONSE:", content)

        return content
