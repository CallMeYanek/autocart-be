import os

from dotenv import load_dotenv

from clients.chat_base import ChatClient

load_dotenv(".env")

# let's define chat client instance first
chat_client = ChatClient()

SMART_SEARCH_API_BASE_URL = os.environ.get("SMART_SEARCH_API_BASE_URL")
SMART_SEARCH_API_URL = f'{SMART_SEARCH_API_BASE_URL}/api/v1/'


def main_loop():
    message = chat_client.get_chat_response()
    print(message)
    print("----------------------------------------------")

    while True:
        prompt = input()
        chat_client.append_user_message(user_prompt=prompt)
        message = chat_client.get_chat_response()
        print("----------------------------------------------")
        print(f"{message}")
        print("----------------------------------------------")


if __name__ == '__main__':
    main_loop()
