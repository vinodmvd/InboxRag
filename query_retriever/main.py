import vector_store
import response_llm
from dotenv import load_dotenv
import os
from textblob import TextBlob
from logger_config import initialize_log_config,get_logger

#Initialize env values
load_dotenv()
index = os.getenv('index')
namespace = os.getenv('namespace')

#Initialize Logger
initialize_log_config()
logger = get_logger(__name__)


def respond_query(getquery, embedding_manager):
    logger.info(f'Query received', extra={'query_length': len(getquery)})
    query_validation = str(TextBlob(getquery).correct())
    embedding = embedding_manager.generate_embeddings(query_validation)
    logger.info(f'Embedding for the query is generated, proceeding with Similarity search')
    query_content = vector_store.search_vector(query_validation, embedding,indexname=index, namespace=namespace)
    response = response_llm.fetch_llm_response(query_content, getquery)
    return response