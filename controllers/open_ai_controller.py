import os
import getpass
from dotenv import load_dotenv
from pydash import get
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from controllers.pinecone_controller import PineconeManager
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from pinecone import Pinecone


os.environ['LANGCHAIN_TRACING_V2'] = os.getenv('LANGSMITH_TRACING_V2')
os.environ['LANGCHAIN_ENDPOINT'] = os.getenv('LANGSMITH_ENDPOINT')
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
os.environ['LANGCHAIN_PROJECT'] = os.getenv('LANGSMITH_PROJECT')
os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY')
embeddings = OpenAIEmbeddings()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

class OpenAiManager:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.pinecone_manager = PineconeManager()


    def generate_response_chain_with_history(self, data):
        try:
            query = get(data, 'query') 
            namespace = get(data, 'namespace') 
            chat_history = get(data, 'chat_history', [])
            vector_store = self.pinecone_manager.get_vectorstore(namespace)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an assistant the learns from website data, answer the user question based on the website data: {context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}")
            ])
            chain = create_stuff_documents_chain(self.llm, prompt)
            retriever = vector_store.as_retriever()
                 
            retriever_prompt = ChatPromptTemplate.from_messages([
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
            ])
            history_aware_retriever = create_history_aware_retriever(self.llm, retriever, retriever_prompt)
            retrieval_chain = create_retrieval_chain(history_aware_retriever, chain)
            chat_history = self.append_history(chat_history)
            response = retrieval_chain.invoke({"chat_history": chat_history, "input": query})
            data['response'] = response
            return data
        except Exception as e:
            print(f"An error occurred during generate response chain with history: {e}")
    

    def generate_response_chain_search_engine(self, data):
        try:
            tool = TavilySearchResults(
                max_results=5,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=True,
                include_images=True,
            )
            response = tool.invoke({"query": data['query']})    
            data['response'] = response   
            return data
        except Exception as e:
            print(f"An error occurred during generate response chain with history: {e}")


    def append_history(self, records):
        print(records)
        chat_history = []
        try:
            for data in records:
                question = str(data.get("question", "") if data.get("question") is not None else "") 
                response = str(data.get("response", "") if data.get("response") is not None else "")            
                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=response))                      
        except Exception as err:
            print("There was an error creating chat history", err)       
        print("chat_history ", chat_history)
        return chat_history

        
        

        
        

















