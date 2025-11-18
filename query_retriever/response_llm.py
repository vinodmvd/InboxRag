from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

op = os.getenv("open_api")

def fetch_llm_response(compose_content, query):
    print(compose_content)
    client = OpenAI(api_key=op)
    full_text = ""
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': f'{compose_content}'},
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
