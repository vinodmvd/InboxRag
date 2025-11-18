from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter

def get_texts_split(rawdata):
    docs = []
    for content in rawdata:
        docs.append(Document(page_content = content['data'], metadata = {'source' : content['filename'], 'months' : content['months'], 'years' : content['years']} ))
    return docs

def text_splitter(data):
    load_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=200)
    splitted_texts = load_splitter.split_documents(data)
    
    texts = []
    for idx, data in enumerate(splitted_texts,start =1):
        
        texts.append(
            {
                'id' : f'id{idx}',
                'metadata' : {
                    'filename' : data.metadata['source'],
                    'chunk_text' : data.page_content,
                    'months' : data.metadata['months'],
                    'years' : data.metadata['years']
                }
            }
        )
        
    total = 0
    for text in texts:
        total=total+len(text['metadata']['chunk_text'])
    print(f'Total number of characters that is going to be embeded: {total}')
    
    return texts