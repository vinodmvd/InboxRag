from pinecone import Pinecone, NotFoundException
import filter_retriever
import reranker
import os

#Initialize Env vars
from dotenv import load_dotenv
load_dotenv()
pi = os.getenv("pine_api")

#Initialize Logger
from logger_config import initialize_log_config, get_logger
initialize_log_config()
logger = get_logger(__name__)

def search_vector(query, embedding, indexname, namespace):
    try:
        load_pine = Pinecone(api_key=pi)
        pine_index_name = f'{indexname}'
        index = load_pine.Index(pine_index_name)
        months, years = filter_retriever.find_months_and_years(query.title())
        
        #First if/else for Namespace validation
        if not months and not years:
            query_output_content = index.query(vector=embedding, top_k=25, namespace=f'{namespace}', include_metadata=True)
        else:
            query_output_content = index.query(vector=embedding, top_k=5, namespace=f'{namespace}', filter={'months' : {'$in': months}, 'years' : {'$in' : years} }, include_metadata=True)
 
        #Namespace exception catches
        if not query_output_content.matches:
            logger.error(f"No vectors returned. Possible invalid namespace: '{namespace}'")
            raise ValueError(f"Pinecone namespace '{namespace}' not found or has no indexed vectors")
        
        #Second if/else for reranker/filter call
        if not months and not years:
            content_reranker = [data.metadata['chunk_text'] for data in query_output_content.matches]
            compose_content = reranker.rerank_data(content_reranker, query)
        else:
            compose_content = [data.metadata['chunk_text'] for data in query_output_content.matches]   
        
        return compose_content
    
    except NotFoundException as e:
        logger.error('Index not found', exc_info=True)
        raise RuntimeError(f'Pinecone index {indexname} not found') from e