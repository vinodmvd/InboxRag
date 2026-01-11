import cohere
import os

def rerank_data(content, query):
    cohere_api = os.getenv('cohere_api')
    co_client = cohere.ClientV2(cohere_api)
    
    response = co_client.rerank(
        model = 'rerank-v3.5',
        query = query,
        documents = content,
        top_n=5
    )
    
    post_rerank = [content[list.index] for list in response.results]

    return post_rerank
