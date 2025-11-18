from sentence_transformers import SentenceTransformer

class EmbeddingManager:

    def __init__(self, model='all-miniLM-L6-V2'):
        self.model = model
        self.load_model = None
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        # print('Initializing Model for embeddings!')
        self.load_model = SentenceTransformer('all-miniLM-L6-V2')
        print(f'Model: {self.model} Initialized')

    def generate_embeddings(self, texts):
        embedding_data_gen = self.load_model.encode(texts)
        embedding_data_gen = embedding_data_gen.tolist()
        # print(f'Total embedded data: {len(embedding_data_gen)}')
        return embedding_data_gen