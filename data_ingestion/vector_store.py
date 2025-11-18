from pinecone import Pinecone,ServerlessSpec
from secret import pinecone as pi
import filter_retriever
import time

def embeddings_to_vector_store(embedding_data, texts, indexname, namespace):
    load_pine = Pinecone(api_key=pi)

    # Index creation on pinecone
    pine_index_name = f'{indexname}'

    if not load_pine.has_index(pine_index_name):
        load_pine.create_index(pine_index_name, vector_type='dense', dimension=384, metric='cosine', spec=ServerlessSpec(cloud='aws',region='us-east-1'))
        print(f'Index: {pine_index_name} is successfully created')
        
    try:
        index = load_pine.Index(pine_index_name)    
        initial_stat_count = index.describe_index_stats().namespaces[f'{namespace}'].vector_count
    except KeyError as e:
        initial_stat_count = 0
    
    for i, item in enumerate(texts):
        item["values"] = embedding_data[i]
    
    print(f'Currently {len(texts)} vectors are going to be upserted!')
    index.upsert(vectors=texts, namespace = f'{namespace}')    
    
    print('Upserts are done, final validation would start in 10 seconds')
    time.sleep(10)
    post_stat_count = index.describe_index_stats().namespaces[f'{namespace}'].vector_count
    new_stat_inserts = post_stat_count - initial_stat_count
        
    # Validation to make sure the chunks were added as expected
    if len(texts) == new_stat_inserts:
        print(f'New inserts: {new_stat_inserts} are successfully completed.\n')
    else:
        print(f'ERROR: Discrepancy on new inserts. Total vector count is not matching post new inserts.\nPlease revalidate. Total new records: {new_stat_inserts} ')  

    print(f'Final Stats:\nInitial-Count: {initial_stat_count}\nNew-Inserts: {len(texts)}\nFinal-Count: {post_stat_count}\n')

def delete_vector(indexname):
    load_pine = Pinecone(api_key=pi)
    if load_pine.has_index(indexname):
        load_pine.delete_index(indexname)
        print(f'Index {indexname} is successfully removed')
    else:
        print('No Index found with provided input.')