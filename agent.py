import os
import json
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from utils import check_college_update, system_message
from langchain.agents import tool


class TransMajor:
    def __init__(self, api_key, base_url, tools, model_name, temperature=0.7):
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        self.model = ChatOpenAI(model=model_name, temperature=temperature, base_url=base_url, api_key=api_key)
        self.tools = tools
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

        # Initialize embeddings and vector store for RAG
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            base_url=base_url,
            api_key=api_key
        )
        self.vectorstore = None  # Will be set after indexing documents

    def query(self, input_query):
        return self.agent_executor.invoke({"input": input_query})

    def document_qa(self, document, question):
        context = f"下面你要根据下面的文档回答问题: {document}\n问题: {question}"
        return self.agent_executor.invoke({"input": context})

    def index_documents(self, documents, persist_directory):
        """
        Indexes a list of documents for retrieval.

        Args:
            documents (List[str]): A list of document texts to index.
            persist_directory (str): Directory to persist the vector store.
        """
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = []
        for doc_text in documents:
            splits = text_splitter.split_text(doc_text)
            docs.extend([Document(page_content=chunk) for chunk in splits])

        # Create a vector store
        self.vectorstore = Chroma.from_documents(docs, self.embeddings, persist_directory=persist_directory)

        # self.vectorstore.persist()

        # Update the retriever tool with the new vector store
        self.add_retriever_tool()

    def add_retriever_tool(self):
        """
        Adds a retriever tool to the agent's tools for RAG functionality.
        """
        if self.vectorstore is None:
            raise ValueError("Vector store is not initialized. Please index documents first.")

        # Create a retriever
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})

        @tool('document_retriever')
        def document_retriever(query: str):
            """用来检索相关文档的工具，输入是查询，输出是相关文档的内容。"""
            print("Retrieving documents for query:", query)
            docs = retriever.invoke(query)
            combined_docs = "\n".join([doc.page_content for doc in docs])
            return combined_docs

        self.tools.append(document_retriever)
        self.agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

    def load_vectorstore(self, persist_directory):
        """
        Loads the persisted vector store from disk.

        Args:
            persist_directory (str): Directory where the vector store is persisted.
        """
        if os.path.exists(persist_directory):
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            # Update the retriever tool with the loaded vector store
            self.add_retriever_tool()
        else:
            raise FileNotFoundError(f"Persist directory not found: {persist_directory}")

    def rag_query(self, question):
        """
        Answers a question using Retrieval-Augmented Generation via the agent executor.

        Args:
            question (str): The question to answer.

        Returns:
            str: The answer generated by the agent.
        """
        if self.vectorstore is None:
            raise ValueError("Vector store is not initialized. Please index documents first.")

        return self.agent_executor.invoke({"input": "你必须调用工具 document_retriever回答这个问题："+question}, tool_choice="auto")


# Main block for testing
if __name__ == "__main__":
    # Initialize TransMajor instance
    trans_major = TransMajor(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_BASE_URL"],
        model_name="gpt-4o-mini-2024-07-18",
        temperature=1,
        tools=[check_college_update]
    )

    # Define the persist directory
    persist_directory = "./vecstore"

    # Try to load the vector store from disk
    try:
        trans_major.load_vectorstore(persist_directory)
        print("Successfully loaded vector store from disk.")
    except FileNotFoundError:
        print("Vector store not found on disk. Indexing documents...")
        # Load documents from JSON file
        document_file = "./data/document.json"
        if os.path.exists(document_file):
            with open(document_file, "r", encoding="utf-8") as f:
                documents = json.load(f)
        else:
            raise FileNotFoundError(f"Document file not found: {document_file}")

        # Index documents and persist the vector store
        trans_major.index_documents(documents, persist_directory=persist_directory)
        print("Documents indexed and vector store persisted.")

    # Example queries
    print("Tool Query:")
    response = trans_major.query("电信学院有文件更新吗？")
    print(response)

    print("RAG Query:")
    response = trans_major.rag_query("请问中德实验班是怎么选拔的？")
    print(response)

    print("Direct Query:")
    response = trans_major.query("我转进了启明班，还能转专业吗？")
    print(response)
