import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from pydash import get
from pinecone import Pinecone, ServerlessSpec
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import OnlinePDFLoader
from db.usage.usage_collection import Usage
from db.records.record_collection import Record

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = 'rapid'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings()


class PineconeManager:
    def __init__(self):
        print("")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.usage_collection = Usage()
        self.record_collection = Record()
        
    def get_vectorstore(self, namespace):
        try:
            indexes = self.pc.list_indexes()
            if len(indexes) == 0:
                print("creating vector store")
                pinecone_retriever = self.pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=1536, 
                    metric="cosine", 
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ) 
                )
            print("index name =>", PINECONE_INDEX_NAME)    
            print("namespace =>", namespace)
            pinecone_retriever = PineconeVectorStore.from_existing_index(
                embedding=embeddings,
                index_name=PINECONE_INDEX_NAME,
                namespace=namespace
            )
            return pinecone_retriever
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None

    def embbed_vectors(self, data):
        try:
            source = get(data, 'source')
            if(source == "website"):
                self.train_by_website(data)
            elif(source == "inputs"):
                self.train_by_input(data)    


        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None 

    def train_by_website(self, data):
        try:
            print("start embbedding website data", data)
            website_url = get(data, 'data') 
            namespace = get(data, 'namespace')  
            tenant_id = get(data, 'tenant_id')
            source = get(data, 'source')
            loader = WebBaseLoader(website_url)
            data = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(data)
            vector_store = self.get_vectorstore(namespace)
            vector_ids = vector_store.add_documents(docs)
            print("vector ids", vector_ids )
            self.db_operations(docs, namespace, tenant_id, website_url, vector_ids)
            print("train by website was successfull")
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None 

    def train_by_input(self, data):
        try:
            print("start embbedding text data", data )
            inputs = get(data, 'data') 
            namespace = get(data, 'namespace')  
            tenant_id = get(data, 'tenant_id')
            source = get(data, 'source')
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.create_documents([inputs])
            vector_store = self.get_vectorstore(namespace)
            vector_ids = vector_store.add_documents(docs)
            print("vector ids", vector_ids )
            self.db_operations(docs, namespace, tenant_id, inputs, vector_ids)
            print("train by inputs was successfull")
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None 

    def db_operations(self, docs, namespace, tenant_id, source, vector_ids):
        try:
            # Assuming 'count_characters' returns the count of characters in the document
            char_count = self.count_characters(docs)
            
            # Create an object to hold properties
            object_data = {
                'docs': docs,
                'namespace': namespace,
                'tenant_id': tenant_id,
                'source': source,
                'key': 'characters_count', ## property name for updating the usage
                'count': char_count,  ## number of data char
                'vector_ids': vector_ids
            }
            
            # Increment usage
            self.usage_collection.increment_usage(object_data)
            
            # Pass the record_data to insert_record_document method
            self.record_collection.insert_record_document(object_data)
        
        except Exception as e:
            # Handle any exceptions here
            print(f"An error occurred: {e}")


       
    def count_characters(self, docs):
        total_char_count = 0
        for doc in docs:
            total_char_count += len(str(docs))      
        return total_char_count

    def delete_vector_data(self, data):
        try:
            namespace = get(data, 'namespace')
            vector_ids = get(data, 'vector_ids')
            vector_store = self.get_vectorstore(namespace)
            vector_store.delete(ids=vectors_ids, namespace=namespace)
            print("vector data was deleted successfully")
        except Exception as e:
            print("error while delete vector data")              