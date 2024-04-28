from pydantic import BaseModel


class ChatData(BaseModel):
    chat_uuid: str
    prompt: str


class StartChatData(BaseModel):
    user_id: str


class ChatResponse(BaseModel):
    chat_uuid: str
    response: dict
