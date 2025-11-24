import generate_embeddings
import vector_store
import response_llm
from dotenv import load_dotenv
import os
from textblob import TextBlob

load_dotenv()
index = os.getenv('index')
namespace = os.getenv('namespace')
def respond_query(getquery, embedding_manager):
    query_validation = str(TextBlob(getquery).correct())
    embedding = embedding_manager.generate_embeddings(query_validation)
    query_content = vector_store.search_vector(query_validation, embedding,indexname=index, namespace=namespace)
    response = response_llm.fetch_llm_response(query_content, getquery)
    return response