# from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.llm.openai_connectivity import OPENAI_API_KEY
from app.rag_chatbot_pipeline.data_handler.raw_pdfs import RawPDFProcessor
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
import os


# from langchain_community.llms import Ollama
# from langchain.chat_models import ChatOpenAI
# from langchain.document_loaders import PyPDFLoader
# from langchain.document_loaders import DirectoryLoader
# from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma

# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory

from langchain.embeddings import HuggingFaceEmbeddings
# from bs4 import BeautifulSoup as Soup
# from langchain.utils.html import (PREFIXES_TO_IGNORE_REGEX,
#                                   SUFFIXES_TO_IGNORE_REGEX)


def prepare_pdf_data():
    processor = RawPDFProcessor()
    return processor.process_all_pdfs()

def load_documents(folder_path):
    """Loads the processed text files and returns a list of Document objects."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The directory '{folder_path}' does not exist.")

    print(f"Loading documents from {folder_path}")
    processed_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith(".txt")]

    if not processed_files:
        print("No processed files found in the directory.")
        return None

    docs = []
    for file_path in processed_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Wrapping raw content in Document objects
            docs.append(Document(page_content=content))
    
    return docs

def split_documents(documents):
    """Splits documents into chunks and stores them in the vector database."""
    
    print(f"Splitting {len(documents)} documents")
    textsplitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=250)
    
    # Now splitting actual Document objects
    chunk_docs = textsplitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)  # Ensure the correct API key is passed
    persist_directory = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store")

    # create embeddings with huggingface embedding model `all-MiniLM-L6-v2`
    # then persist the vector index on vector db
    # try:
    #     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    #     database = Chroma.from_documents(
    #         documents=documents,
    #         embedding=embeddings,
    #         persist_directory=persist_directory
    #     )
    #     database.persist()
    try:
        database = Chroma.from_documents(
            documents=chunk_docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise

    print({"collection count": database._collection.count()})
    return database

async def initialize_vector_database():
    folder_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "processed_pdfs")
    try:
        prepare_pdf_data()  # Ensure PDFs are processed
        
        docs = load_documents(folder_path)
        if docs:
            return split_documents(docs)
        else:
            print("No documents were found to initialize the vector database.")
            return None
    except Exception as e:
        print(f"Error initializing vector database: {e}")
        return None

