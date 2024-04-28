import json

import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379

redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

CHAT_CONTEXT_PREFIX = "CHAT"
USER_ID_PREFIX = "USER"


class RedisClient:
    def set_key(self, key, value):
        redis.set(key, value)

    def get_key(self, key):
        return redis.get(key)

    def save_conversation_context(self, chat_uuid: str, conversation_context: list[dict]):
        conversation_context_raw = json.dumps(conversation_context)
        self.set_key(chat_uuid, conversation_context_raw)

    def save_chat_user_id(self, chat_uuid: str, user_id: str):
        self.set_key(f"{USER_ID_PREFIX}_{chat_uuid}", user_id)

    def get_user_id_by_chat_uuid(self, chat_uuid: str) -> str:
        user_id = self.get_key(f"{USER_ID_PREFIX}_{chat_uuid}")
        return user_id
