"""
Used by main_iter_2
"""
import os

from openai import OpenAI


class ChatClient:
    def __init__(self):
        """
        Init OpenAI Client
        Init predefined chat context with chat system instructions
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        self.conversation_context: list[dict] = [
            {
                "role": "system",
                "content": f"""You are a helpful shopping assistant.
                You can (but don't have to) carry on conversation before and after providing a recipes/shopping list by asking user/telling him/her somehow.
                You speak mainly Polish.
                Your tasks is to help user find products it wants, and if user wants it too - find recipes.
                To achieve that keep following few rules:
                If user mentioned its preferences (for example: I want vegan breakfast), get products based on that mentioned preferences.
                Start conversation with asking user how can you help him/her somehow.
                """
            },
        ]

    def append_user_message(self, user_prompt: str) -> None:
        """
        Adds user prompt to conversation context
        """
        user_message = {"role": "user", "content": user_prompt}
        self.conversation_context.append(user_message)

    def get_chat_response(self) -> (str, list):
        """
        Get gpt response using chat completions and pass it to response processing
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[message for message in self.conversation_context],
                max_tokens=2500,
                n=1,
                stop=None,
                temperature=0.1,
            )
        except Exception as e:
            raise e

        message = self.api_response_processing(completion)
        return message

    def api_response_processing(self, completion) -> str:
        """
        Process chat completion by accessing message content, clean it and append to conversation context
        """
        content = completion.choices[0].message.content
        message = content.strip()
        self.conversation_context.append({"role": "assistant", "content": message})
        return message
