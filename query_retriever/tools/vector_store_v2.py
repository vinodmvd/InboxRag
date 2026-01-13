from query_retriever.reranker import rerank_data
from query_retriever.logger_config import initialize_log_config, get_logger

initialize_log_config()
logger = get_logger(__name__)


def semantic_search(index, namespace, vector, tool_args):
    logger.info("Performing Semantic Search")
    result = index.query(
        namespace = namespace,
        vector = vector, 
        top_k = tool_args['top_k'],
        include_metadata = True,
        include_values = False,
    )
    
    logger.info(f"Revalidated query: {tool_args['validated_query']}")
    logger.info("Proceeding with reranking")
    text_reranker = [data['metadata']['chunk_text'] for data in result.matches]
    
    return rerank_data(text_reranker, tool_args['validated_query'])
    
    
    
def filter_search(index, namespace, vector, tool_args):
    logger.info("Performing Filtering Search")
    
    result = index.query(
        namespace= namespace,
        vector = vector,
        top_k = tool_args['top_k'],
        filter = tool_args['filter'],
        include_metadata = True,
        include_values = False
    )
    
    logger.info(f"Revalidated query: {tool_args['validated_query']}")
    
    return result