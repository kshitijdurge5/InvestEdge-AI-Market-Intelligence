from openai import OpenAI


from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
)

from .prompts import SYSTEM_PROMPT


class DeepSeekClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )

        self.model = DEEPSEEK_MODEL

    def chat(self, message: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": message,
                            },
                            ],
                            )
                            
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't process your request. Error: {e}"