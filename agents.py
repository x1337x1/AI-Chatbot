import os
import getpass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from controllers.pinecone_controller import PineconeManager
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.tools.retriever import create_retriever_tool
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from dotenv import load_dotenv
load_dotenv()



llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.7)
pinecone_manager = PineconeManager()


search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search)

def generate_response_chain_with_agents(namespace):
    vector_store = pinecone_manager.get_vectorstore(namespace)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    retriever = vector_store.as_retriever() ## method that we use to get documents from pinecone
    retriever_tool = create_retriever_tool(retriever, "langsmith_search", "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!")
    tools = [retriever_tool, tavily_tool]
    agent_prompt = hub.pull("hwchase17/openai-functions-agent") ## prompt
    agent = create_openai_functions_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


def process_chat(agent_executor, question, chat_history):
    response = agent_executor.invoke({
        "chat_history": chat_history,
        "input": question,
    })
    return response


if __name__ == "__main__":
    agent = generate_response_chain_with_agents("langsmith_namespace")
    # Initialize chat history
    chat_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = process_chat(agent, user_input, chat_history)
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content= str(response) ))
        print("Assistant:", response)