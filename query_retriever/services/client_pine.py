import os

from pinecone import Pinecone, NotFoundException

class VectorInitializer():
    
    def __init__(self,name):
        pine_api = os.getenv('pine_api')
        self.loader = Pinecone(api_key=pine_api)
        self.indexname = name
    
    def check_index_existence(self):
        try:
            index = self.loader.Index(name=self.indexname)
            print('Index exists')
            return index
        except NotFoundException as err:
            print('Index not found, please try again {}'.format(err))
            
if __name__ == "__main__":
    vector_init = VectorInitializer(name='mydataa')
    