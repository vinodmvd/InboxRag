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
    
    logger.info(f"User query: {query}")
    
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
    
    if response.choices[0].message.tool_calls:
        for tool in response.choices[0].message.tool_calls:
            function_name = tool.function.name
            function_args = json.loads(tool.function.arguments)
            
            if function_name == 'semantic_search' or function_name == 'filter_search':
                return function_name, function_args
    else:
        print(response.choices[0].message.content)
        logger.info("No function was assigned by the agent. {}".format(response.choices[0].message.content))