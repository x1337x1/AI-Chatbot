import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from pinecone import Pinecone, ServerlessSpec
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import OnlinePDFLoader

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = 'rapid'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings()


class PineconeManager:
    def __init__(self):
        print("")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
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

    def embbed_vectors(self, data, source, namespace):
        try:
            if(source == "website"):
                self.train_by_website(data, namespace)
            elif(source == "inputs"):
                self.train_by_input(data, namespace)    


        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None 

    def train_by_url(self, data):
        try:
            # Extract website_url and namespace from the data object
            website_url = data.get('website_url')
            namespace = data.get('namespace')
    
            # Validate the input
            if not website_url or not namespace:
                raise ValueError("Missing 'website_url' or 'namespace' in the data object")
    
            print("start embedding website data")
            loader = WebBaseLoader(website_url)
            page_data = loader.load()
            
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(page_data)
            
            # Retrieve the vector store using the namespace
            vector_store = self.get_vectorstore(namespace)
            vector_store.add_documents(docs)
            
            print("Training by website was successful")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None


    def train_by_input(self, data):
        try:
            text = data.get('input')
            namespace = data.get('namespace')
            if not text or not namespace:
                raise ValueError("Missing 'input' or 'namespace' in the data object")
    
            print("start embedding text data")
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.create_documents([text])
            
            # Retrieve the vector store using the namespace
            vector_store = self.get_vectorstore(namespace)
            vector_store.add_documents(docs)
            
            print("Training by input was successful")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None
