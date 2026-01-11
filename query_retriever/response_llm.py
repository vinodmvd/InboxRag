from openai import OpenAI
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

#Env vars
op = os.getenv("open_api")

base_dir = Path(__file__).resolve().parent/'prompt.txt'

with open(base_dir, "r", encoding="utf-8") as f:
    input_prompt = f.read()

def fetch_llm_response(compose_content, query):
    client = OpenAI(api_key=op)
    full_text = ""
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': f'{input_prompt}\n{compose_content}'},
            {'role': 'user', 'content': f'{query}'}
        ],
        stream=True,
        temperature=0.2
    )

    for chunk in response:
        if hasattr(chunk, 'choices'):
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content 
