from langchain_openai import OpenAIEmbeddings, OpenAI
from app.openai.openai_connectivity import OPENAI_API_KEY  # Ensure correct import
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import os

# Module 1: Document Retrieval
async def document_retrieval(query, vector_database):
    """Retrieves documents using MMR and similarity search from a vector database."""
    mmr_retriever = vector_database.as_retriever(search_kwargs={"k": 3})
    
    try:
        ss_retrieved_documents = await vector_database.similarity_search(query, k=3)
        mmr_retrieved_documents = await mmr_retriever.invoke(query)

        # Combine and deduplicate documents
        all_retrieved_documents = mmr_retrieved_documents + ss_retrieved_documents
        all_retrieved_documents = list({doc.page_content: doc for doc in all_retrieved_documents}.values())
        return all_retrieved_documents
    except Exception as e:
        print(f"Error in document retrieval: {e}")
        return []

# Module 2: Vector Database Initialization
def initialize_vector_database():
    """Initializes and returns a Chroma vector database with OpenAI embeddings."""
    embeddings = OpenAIEmbeddings(openai_api_type=OPENAI_API_KEY)
    directory_to_persist = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store")
    vector_database = Chroma(
        persist_directory=directory_to_persist,
        embedding_function=embeddings
    )
    
    print({'Collection count': vector_database._collection.count()})
    return vector_database

# Module 3: Compression Retriever Initialization
def initialize_compression_retriever(vector_database):
    """Initializes and returns a ContextualCompressionRetriever for document compression."""
    llm = OpenAI(api_key=OPENAI_API_KEY)
    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=vector_database.as_retriever(search_type="mmr")
    )
    return compression_retriever

# Module 4: Retrieval and Compression
async def retrieve_and_compress_documents(query, all_retrieved_documents, compression_retriever):
    """Retrieves and compresses documents using the compression retriever."""
    all_retrieved_documents = [doc.page_content for doc in all_retrieved_documents]
    compressed_docs = await compression_retriever.invoke(query, context=all_retrieved_documents)
    pretty_print_docs(compressed_docs)
    return compressed_docs

# Helper Function
def pretty_print_docs(docs):
    """Prints the document contents in a more readable format."""
    print(f"\n{'-' * 100}\n".join([f"Document {i + 1}:\n\n" + d.page_content for i, d in enumerate(docs)]))

# Main Execution (For testing or standalone use)
if __name__ == "__main__":
    import asyncio  # Import asyncio to run async functions

    async def main():
        vector_database = initialize_vector_database()
        query = "What programs does the university offer?"
        all_retrieved_documents = await document_retrieval(query, vector_database)
        compression_retriever = initialize_compression_retriever(vector_database)
        await retrieve_and_compress_documents(query, all_retrieved_documents, compression_retriever)

    # Run the main function using asyncio
    asyncio.run(main())
