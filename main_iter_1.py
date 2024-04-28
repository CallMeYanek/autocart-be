import os

from dotenv import load_dotenv

from openai import OpenAI

load_dotenv(".env")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# predefined chat context
chat_context = [
    {"role": "system", "content": "You are a helpful assistant designed to answer questions."},
    {"role": "user", "content": "Who won the F1 in 2022?"}
]

while True:
    resp = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=chat_context,
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=0.1,
    )
    chat_response_message = resp.choices[0].message.content
    chat_context.append({"role": "assistant", "content": chat_response_message})

    print(chat_response_message)

    user_prompt = input("User: ")

    chat_context.append({"role": "user", "content": user_prompt})
