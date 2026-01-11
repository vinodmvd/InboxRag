from sentence_transformers import SentenceTransformer

from query_retriever.logger_config import get_logger,initialize_log_config

initialize_log_config()
logger = get_logger(__name__)

class EmbeddingManager:

    def __init__(self, model='all-miniLM-L6-V2'):
        self.model = model
        self.load_model = None
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        logger.info('Loading embedding model..')
        self.load_model = SentenceTransformer('all-miniLM-L6-V2')
        logger.info(f'Model Initiated: {self.model}')

    def generate_embeddings(self, texts):
        embedding_data_gen = self.load_model.encode(texts)
        embedding_data_gen = embedding_data_gen.tolist()
        logger.info(f'Documents embedded: {len(texts)}')
        return embedding_data_gen