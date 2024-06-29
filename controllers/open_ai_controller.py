import os
from dotenv import load_dotenv
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
from pinecone import Pinecone


embeddings = OpenAIEmbeddings()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

class OpenAiManager:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.pinecone_manager = PineconeManager()

    def generate_similarity_response(self, query, namespace):
        print("generating a response")
        vector_store = self.pinecone_manager.get_vectorstore(namespace)
        search = vector_store.similarity_search(query)
        answer = search[0].page_content
        return answer


    def generate_response_chain(self, query, role, namespace):
        vector_store = self.pinecone_manager.get_vectorstore(namespace)
        retriever = vector_store.as_retriever()
        prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:
        <context>
        {context}
        </context> 
        Question: {input}""")
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response = retrieval_chain.invoke({"input": query})
        print("answer => ",response["answer"])
        return response["answer"]


    def generate_response_chain_with_history(self, question, namespace, records):
        try:
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
            chat_history = self.append_history(records)
            response = retrieval_chain.invoke({"chat_history": chat_history, "input": question})
            return response["answer"]
        except Exception as e:
            print(f"An error occurred during generate response chain with history: {e}")
    

    def append_history(self, records):
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

        
        

        
        

















