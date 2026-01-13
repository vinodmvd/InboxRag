import os

import query_retriever.response_llm as response_llm
from query_retriever.logger_config import initialize_log_config,get_logger
from query_retriever.services.client_pine import VectorInitializer
from query_retriever.tools.vector_store_v2 import semantic_search, filter_search
from query_retriever.agent.controller import user_query


#Initialize env values
indexname = os.getenv('index')
namespace = os.getenv('namespace')

#Initialize Logger
initialize_log_config()
logger = get_logger(__name__)


def respond_query(getquery, embedding_manager):
    logger.info(f'Query received', extra={'query_length': len(getquery)})
    embedding = embedding_manager.generate_embeddings(getquery)
    tool_name, tool_args = user_query(getquery)
    vector_initializer = VectorInitializer(name=indexname)
    index = vector_initializer.check_index_existence()
    logger.info(f'Embedding for the query is generated. LLM would decide on the search')
    
    if tool_name == 'filter_search':
        query_content = filter_search(index=index, namespace=namespace, vector=embedding, tool_args=tool_args)
        response = response_llm.fetch_llm_response(query_content, getquery)
    elif tool_name == 'semantic_search':
        query_content = semantic_search(index=index, namespace=namespace, vector=embedding, tool_args=tool_args)
        response = response_llm.fetch_llm_response(query_content, getquery)
    elif tool_name == 'NO_TOOL':
        response = response_llm.fetch_llm_response(getquery)
        
    logger.info('LLM is being provided with content, query!')
    return response