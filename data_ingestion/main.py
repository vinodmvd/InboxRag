from pathlib import Path
base_dir = Path(__file__).resolve().parents[1]

from dotenv import load_dotenv
load_dotenv(base_dir/".env")

# import gmail_extract
import gmail_extract_v2
import gmail_load_split
import generate_embeddings
import vector_store
import getpass

if __name__ == "__main__":
    myask = 'adddoc'
            
    if 'adddoc' in myask:
        print('Note: You\'re going to insert documents to Pinecone DB')
        docpass = getpass.getpass('Please enter your password for doc: ')
        getindexname = input('Please enter the Index name for Vector DB: ')
        getnamespace = input('Please enter the namespace for the index: ')
        subjectname = input('Enter the subject name from email to extract: ')   
        # get_gmail_content = gmail_extract.main(docpass, subjectname)
        get_gmail_content = gmail_extract_v2.main(docpass, subjectname)
        getdocuments = gmail_load_split.get_texts_split(get_gmail_content)
        getsplitted = gmail_load_split.text_splitter(getdocuments)
        embedding_manager = generate_embeddings.EmbeddingManager()
        embedding_data = embedding_manager.generate_embeddings(getsplitted)
        vector_store.embeddings_to_vector_store(embedding_data, getsplitted, getindexname, getnamespace)
        
    elif 'deldoc' in myask:
        print('WARNING: This operation is going to remove the specfied vector from Pinecone DB')
        getname = input('Enter the name of the index to be removed: ')    
        vector_store.delete_vector(getname)