from query_retriever.reranker import rerank_data


def semantic_search(index, namespace, vector, tool_args):
    result = index.query(
        namespace = namespace,
        vector = vector, 
        top_k = tool_args['top_k'],
        include_metadata = True,
        include_values = False,
    )
    
    text_reranker = [data['metadata']['chunk_text'] for data in result.matches]
    
    return rerank_data(text_reranker, tool_args['validated_query'])
    
    
    
def filter_search(index, namespace, vector, tool_args):
    result = index.query(
        namespace= namespace,
        vector = vector,
        top_k = tool_args['top_k'],
        filter = tool_args['filter'],
        include_metadata = True,
        include_values = False
    )
    
    return result