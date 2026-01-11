from query_retriever.services.client_openai import client
from query_retriever.agent.system_prompt import prompt_ai


def user_query(query):
    
    TOOL = []
    
    
    messages = [
        {"role" : "user", "content" : query},
        {"role" : "system" , "content" : prompt_ai}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = messages,
        tools=TOOL,
        tool_choice="auto"
    )