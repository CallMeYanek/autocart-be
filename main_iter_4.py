import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clients.chat import ChatClient
from clients.redis import RedisClient
from models.models import ChatResponse, ChatData, StartChatData

load_dotenv(".env")

chat_client = ChatClient()

# define FastAPI application
app = FastAPI()

# TODO: Only for local development, change before release
# we shouldn't allow all methods, origins and headers when releasing production app (security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SMART_SEARCH_API_BASE_URL = os.environ.get("SMART_SEARCH_API_BASE_URL")
SMART_SEARCH_API_URL = f'{SMART_SEARCH_API_BASE_URL}/api/v1/'

redis_client = RedisClient()


# that method (view) will be executed every time, someone will call /start-chat endpoint using POST method and proper data
@app.post('/start-chat', response_model=ChatResponse)
def start_chat_endpoint(data: StartChatData):
    chat_uuid, message, conversation_context = chat_client.start_chat(data.user_id)
    redis_client.save_conversation_context(chat_uuid, conversation_context)

    redis_client.save_chat_user_id(chat_uuid, data.user_id)

    formatted_message = json.loads(message)
    return {
        'chat_uuid': chat_uuid,
        'response': formatted_message,
    }


# that method (view) will be executed every time, someone will call /chat endpoint using POST method and proper data
@app.post('/chat', response_model=ChatResponse)
def chat_endpoint(data: ChatData):
    chat_uuid = data.chat_uuid
    conversation_context_raw = redis_client.get_key(chat_uuid)
    user_id = redis_client.get_user_id_by_chat_uuid(chat_uuid)
    conversation_context = json.loads(conversation_context_raw)

    prompt = data.prompt
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
    return {
        'chat_uuid': chat_uuid,
        'response': message
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8888)  # start web application
