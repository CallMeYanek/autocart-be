import json
import os

from dotenv import load_dotenv

from clients.chat import ChatClient
from clients.redis import RedisClient
from utils.utils import timeit

load_dotenv(".env")

chat_client = ChatClient()


SMART_SEARCH_API_BASE_URL = os.environ.get("SMART_SEARCH_API_BASE_URL")
SMART_SEARCH_API_URL = f'{SMART_SEARCH_API_BASE_URL}/api/v1/'

# redis is in-memory database with simple structure (key - value).
# Here I'm using it just to keep conversation context assigned to specific conversation uuid.
# Not really needed full understanding it
redis_client = RedisClient()


def start_chat(user_id: str) -> (str, dict):
    """
    Call start chat method from chat client
    Save conversation context into redis DB
    """
    chat_uuid, message, conversation_context = chat_client.start_chat(user_id)
    redis_client.save_conversation_context(chat_uuid, conversation_context)

    redis_client.save_chat_user_id(chat_uuid, user_id)

    formatted_message = json.loads(message)
    return chat_uuid, formatted_message


@timeit
def chat(chat_uuid, prompt):
    """
    Get conversation context based on uuid.
    Append user message and get chat response
    At the end, save updated conversation context to Redis DB again
    """
    conversation_context_raw = redis_client.get_key(chat_uuid)
    user_id = redis_client.get_user_id_by_chat_uuid(chat_uuid)
    conversation_context = json.loads(conversation_context_raw)

    conversation_context = chat_client.append_user_message(
        user_prompt=prompt,
        conversation_context=conversation_context
    )

    message, conversation_context = chat_client.get_chat_response(
        conversation_context=conversation_context,
        user_id=user_id,
    )

    redis_client.save_conversation_context(chat_uuid, conversation_context)

    message = json.loads(message)
    return chat_uuid,  message


def main_loop():
    chat_uuid, message = start_chat("user_2")
    print(message)
    print("----------------------------------------------")

    while True:
        prompt = input()
        chat_uuid, response = chat(chat_uuid, prompt)
        print("----------------------------------------------")
        print(f"{response}")
        print("----------------------------------------------")


# # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main_loop()
