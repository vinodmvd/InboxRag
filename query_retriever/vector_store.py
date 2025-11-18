from pinecone import Pinecone
import filter_retriever
import os
from dotenv import load_dotenv
load_dotenv()


pi = os.getenv("pine_api")
raw_prompt = os.getenv("input_prompt")
input_prompt = raw_prompt.replace('\\n', '\n') if raw_prompt else ""

def search_vector(query, embedding, indexname, namespace):
    load_pine = Pinecone(api_key=pi)
    pine_index_name = f'{indexname}'
    index = load_pine.Index(pine_index_name)
    months, years = filter_retriever.find_months_and_years(query.title())
    if not months and not years:
        query_output_content = index.query(vector=embedding, top_k=5, namespace=f'{namespace}', include_metadata=True)
    else:
        query_output_content = index.query(vector=embedding, top_k=5, namespace=f'{namespace}', filter={'months' : {'$in': months}, 'years' : {'$in' : years} }, include_metadata=True)
    
    compose_content = []
    for data in query_output_content.matches:
        compose_content.append(f"{data.metadata['chunk_text']}{input_prompt}")
    return compose_content