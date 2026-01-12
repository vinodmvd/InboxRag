import json

from query_retriever.services.client_openai import client
from query_retriever.agent.system_prompt import prompt_ai
from query_retriever.logger_config import initialize_log_config, get_logger

initialize_log_config()
logger = get_logger(__name__)

def user_query(query):
    
    TOOL = [
    {
        "type" : "function",
        "function" : {
            "name" : "semantic_search",
            "description" : "Random queries from users, which does not have categorization words, semantic search would be applied.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "top_k" : {
                        "type" : "number"
                    },
                    "validated_query" : {
                        "type" : "string"
                    }
                },
                "required" : ["top_k", "validated_query"]
            }
        }
    },
    {
        "type" : "function",
        "function" : {
            "name" : "filter_search",
            "description" : "When user query contains months, years, then filtering search would be applied",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "top_k" : {
                        "type" : "number"
                    },
                    "validated_query" : {
                        "type" : "string"
                    },
                    "filter" :{
                        "type" : "object",
                        "properties" : {
                            "months" :{
                                "type" : "object",
                                "properties" : {
                                    "$in" : {
                                        "type" : "array",
                                        "items" : {
                                            "type" : "string"
                                        }
                                    }
                                },
                                "required" : ["$in"]
                            },
                            "years" : {
                                "type" : "object",
                                "properties" : {
                                    "$in" : { 
                                        "type" : "array",
                                        "items" : {
                                            "type" : "string"
                                        }
                                    }
                                },
                                "required" : ["$in"]
                            }
                        },
                        "required" : ["months" , "years"]
                    }
                },
                "required" : ["top_k", "validated_query", "filter"]
            }
        }            
    }]
    
    
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
    
    # ChatCompletion(id='chatcmpl-Cx66TYfK4wPuPGHMFuDbcHSOvkSU2', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_oiM8Bw8Fy5lsi79B6pSKo6wF', function=Function(arguments='{"top_k":5,"validated_query":"bill for January 2024","filter":{"months":{"$eq":"January"},"years":{"$eq":2024}}}', name='filter_search'), type='function')]))], created=1768200849, model='gpt-4o-mini-2024-07-18', object='chat.completion', service_tier='default', system_fingerprint='fp_29330a9688', usage=CompletionUsage(completion_tokens=44, prompt_tokens=382, total_tokens=426, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))
    
    print(response)
    if response.choices[0].message.tool_calls:
        for tool in response.choices[0].message.tool_calls:
            function_name = tool.function.name
            function_args = json.loads(tool.function.arguments)
            
            if function_name == 'semantic_search' or function_name == 'filter_search':
                return function_name, function_args
    else:
        print(response.choices[0].message.content)
        logger.info("No function was assigned by the agent. {}".format(response.choices[0].message.content))