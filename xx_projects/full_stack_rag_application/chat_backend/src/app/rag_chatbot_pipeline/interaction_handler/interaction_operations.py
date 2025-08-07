from langchain_openai import OpenAIEmbeddings
from app.openai.openai_connectivity import OPENAI_API_KEY  # Assuming correct import
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains.summarize import load_summarize_chain

import os

# Module 1: Document Retrieval
def document_retrieval(query, vector_database):
    """Retrieves documents using MMR and similarity search from a vector database."""

    mmr_retriever = vector_database.as_retriever(search_kwargs={"k": 3})
    ss_retrieved_documents = vector_database.similarity_search(query, k=3)
    mmr_retrieved_documents = mmr_retriever.invoke(query)

    # (Optional) Print statements for debugging
    print({'mmr_retrieved_documents length': len(mmr_retrieved_documents)})
    print({'ss_retrieved_documents length': len(ss_retrieved_documents)})
    print({'mmr_retrieved_documents': mmr_retrieved_documents[0].page_content[:500]})
    print({'ss_retrieved_documents': ss_retrieved_documents[0].page_content[:500]})

    # Combine and deduplicate documents
    all_retrieved_documents = mmr_retrieved_documents + ss_retrieved_documents
    all_retrieved_documents = list({doc.page_content: doc for doc in all_retrieved_documents}.values())

    # (Optional) Print statements for debugging
    print({'all_retrieved_documents length': len(all_retrieved_documents)})
    for i, doc in enumerate(all_retrieved_documents):
        print(f'Document {i + 1} from combined results: {doc.page_content[:500]}')

    return all_retrieved_documents


# Module 2: Vector Database Initialization
def initialize_vector_database():
    """Initializes and returns a Chroma vector database with OpenAI embeddings."""

    embeddings = OpenAIEmbeddings(openai_api_type=OPENAI_API_KEY)
    directory_to_persist = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store")
    vector_database = Chroma(
        persist_directory=directory_to_persist,
        embedding_function=embeddings
    )

    # (Optional) Print statement for debugging
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
def retrieve_and_compress_documents(query, all_retrieved_documents, compression_retriever):
    """Retrieves and compresses documents using the compression retriever."""
    all_retrieved_documents = [doc.page_content for doc in all_retrieved_documents]
    compressed_docs = compression_retriever.invoke(query, context=all_retrieved_documents)
    pretty_print_docs(compressed_docs)  # (Optional) Print compressed docs
    return compressed_docs, all_retrieved_documents



# Helper Function
def pretty_print_docs(docs):
    """Prints the document contents in a more readable format."""
    print(f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]))



# Main Execution
if __name__ == "__main__":
    vector_database = initialize_vector_database()
    query = "what programs does the university offers?"
    all_retrieved_documents = document_retrieval(query, vector_database)
    compression_retriever = initialize_compression_retriever(vector_database)
    retrieve_and_compress_documents(query, all_retrieved_documents, compression_retriever)
