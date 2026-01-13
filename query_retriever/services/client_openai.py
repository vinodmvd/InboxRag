import os

from openai import OpenAI

open_api = os.getenv('open_api')

client = OpenAI(api_key=open_api)