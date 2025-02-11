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

    def train_by_website(self, website_url, namespace):
        try:
            print("start embbedding website data")
            loader = WebBaseLoader(website_url)
            data = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(data)
            vector_store = self.get_vectorstore(namespace)
            vector_store.add_documents(docs)
            print("train by website was successfull")
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None 

    def train_by_input(self, text, namespace):
        try:
            print("start embbedding text data")
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.create_documents([text])
            vector_store = self.get_vectorstore(namespace)
            vector_store.add_documents(docs)
            print("train by inputs was successfull")
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            return None 