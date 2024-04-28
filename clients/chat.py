"""
Used by main_iter_3 and main_iter_4
"""
import json
import os
import uuid

from openai import OpenAI

from clients.smart_search import SmartSearchClient


class ChatClient:
    def __init__(self):
        """
        Init OpenAI Client
        Init smart search client
        Init available chat functions dict
        Init tools (functions) description that will be passed to gpt client
        Init predefined chat context with chat system instructions
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        self.smart_search_client = SmartSearchClient()
        self.functions = {
            'get_products': self.smart_search_client.get_products,
        }
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_products",
                    "description": "Get the products list based on tags.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "string",
                                "enum": ["vege", "vegan", "vegetables", "fruits", "bread", "dairy", "drinks", "meat"],
                                "description": "Product tag",
                            },
                        },
                        "required": ["tags", ],
                    },
                }
            }
        ]

        self.conversation_context: list[dict] = [
            {
                "role": "system",
                "content": f"""You are a helpful shopping assistant designed to output in json format.
                Json keys should be in english.
                If you are describing shopping list, use "shopping_list" key in json.
                Please, return to user, the whole product you received from get_products function.
                You can (but don't have to) carry on conversation before and after providing a recipes/shopping list by asking user/telling him somehow. 
                If you're talking to user in that way, use "message_x" key in json where x is number of message_key in one response to user (for example message_1, message_2 etc.)
                If you are describing recipe, use "message_x" key in json like in a normal message.
                You mainly speak Polish.
                Your tasks is to help user find products it wants, and if user wants it to - find recipes.
                To achieve that keep following few rules:
                If user mentioned its preferences (for example: I want vegan breakfast), get products based on that mentioned preferences.
                Start conversation with asking user how can you help him/her somehow.
                """
            },
        ]

    def start_chat(self, user_id: str) -> (str, str, list):
        """
        Prepare conversation
        Generate chat uuid that will be used to identify specific conversation
        Copy base chat context
        Get first chat response that inits the conversation
        """
        chat_uuid = str(uuid.uuid4())
        conversation_context = self.conversation_context.copy()

        message, updated_conversation_context = self.get_chat_response(conversation_context, user_id)
        return chat_uuid, message, updated_conversation_context

    def append_user_message(self, user_prompt: str, conversation_context: list):
        """
        Adds user prompt to conversation context
        """
        user_message = {"role": "user", "content": user_prompt}
        conversation_context.append(user_message)
        return conversation_context

    def get_chat_response(self, conversation_context: list, user_id: str) -> (str, list):
        """
        Get gpt response using chat completions and pass it to response processing
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4-turbo",
                response_format={"type": "json_object"},
                messages=[message for message in conversation_context],
                max_tokens=2500,
                tools=self.tools,
                n=1,
                stop=None,
                temperature=0.1,
            )
        except Exception as e:
            raise e

        message, conversation_context = self.api_response_processing(completion, conversation_context, user_id)
        return message, conversation_context

    def api_response_processing(self, completion, conversation_context, user_id):
        """
        Process chat completion by accessing message content, clean it and append to conversation context
        In case function call is needed, process it using 'function_call_processing' method
        """
        message = None
        completion_message = completion.choices[0].message
        if content := completion_message.content:
            message = content.strip()
            conversation_context.append({"role": "assistant", "content": message})
        elif tool_calls := completion_message.tool_calls:
            _completion_message = {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "arguments": tool_call.function.arguments,
                            "name": tool_call.function.name,
                        }
                    } for tool_call in tool_calls
                ]
            }
            conversation_context.append(_completion_message)
            for tool_call in tool_calls:
                conversation_context = self.function_call_processing(tool_call, conversation_context, user_id)
            message, conversation_context = self.get_chat_response(conversation_context, user_id)
        return message, conversation_context

    def function_call_processing(self, function_call, conversation_context, user_id) -> dict:
        """
        Process chat message that needs function call
        Get function name, get it from already defined (__init__) functions, call it using params chat asked,
        add response to conversation context
        """
        function_name = function_call.function.name
        function_kwargs = json.loads(function_call.function.arguments)
        function = self.functions[function_name]
        function_result = function(**function_kwargs, user_id=user_id)
        function_chat_message = {
            'role': 'tool',
            'tool_call_id': function_call.id,
            'name': function_name,
            'content': json.dumps(function_result),
        }
        conversation_context.append(function_chat_message)
        return conversation_context
