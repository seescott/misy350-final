import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIChatAssistant:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def generate_response(self, question, user_expenses):
        if self.client is None:
            return "OpenAI API key was not found."

        expense_text = str(user_expenses)

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant for an expense tracker app. Help the user understand their spending based only on their expense data."
                },
                {
                    "role": "user",
                    "content": f"My expenses are: {expense_text}. My question is: {question}"
                }
            ]
        )

        return response.choices[0].message.content