import asyncio

from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.rag_chatbot_pipeline.data_handler.data_operations import load_documents, split_documents
from app.rag_chatbot_pipeline.interaction_handler.interaction_operations import initialize_compression_retriever, document_retrieval, initialize_vector_database, retrieve_and_compress_documents

from app.openai.openai_connectivity import OPENAI_API_KEY
import os

vector_database = None  
compression_retriever = None

async def load_and_initialize_vector_database():
    global vector_database
    if not vector_database:
        folder_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
        docs = load_documents(folder_path)
        vector_database = split_documents(docs)
    else:
        vector_database = initialize_vector_database()

async def question_answer(query, chat_history=None, chain_type="stuff"):
    """Answers a question based on the content of documents and chat history.

    Args:
        query (str): The question to answer.
        chat_history (list, optional): List of previous chat interactions. Defaults to None.

    Returns:
        dict: A dictionary containing the answer and source documents.
    """

    await load_and_initialize_vector_database()

    global vector_database
    all_retrieved_documents = document_retrieval(query, vector_database)
    all_retrieved_documents = [doc.page_content for doc in all_retrieved_documents]

    global compression_retriever
    if not compression_retriever:
        compression_retriever = initialize_compression_retriever(vector_database)

    # NOTE : Do not remove any comments. they are method that can be used if needed.
    # compressed_retriever, all_retrieved_documents = retrieve_and_compress_documents(query=query, all_retrieved_documents=all_retrieved_documents, compression_retriever=compression_retriever)

    template = """You are Dawood University's assistant chatbot. Use the following pieces of context to answer the question at the end and instructions given to you here. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Greet properly in response to a greet.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    if chat_history:
        for message in chat_history:
            if message["role"] == "user":
                memory.chat_memory.add_user_message(message["content"])
            elif message["role"] == "assistant":
                memory.chat_memory.add_ai_message(message["content"])

    if chat_history:
        qa = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
            retriever=compression_retriever,
            memory=memory,
            chain_type_kwargs={'prompt': QA_CHAIN_PROMPT},
        )
    else:
        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
            chain_type=chain_type,
            retriever=compression_retriever,
            chain_type_kwargs={'prompt': QA_CHAIN_PROMPT},
            return_source_documents=True,
            verbose=True
        )
    
    # Using ainvoke instead of arun
    response = await qa.ainvoke({"query": query}, {"context": all_retrieved_documents})
    
    # Extracting result and source_document from response
    result = response.get("result")
    source_documents = response.get("source_documents", [])
    
    # Returning a dictionary containing the result and source_documents
    return {"result": result, "source_documents": source_documents}

async def main():
    query = "What is the name of university?"
    response = await question_answer(query)
    
    result = response["result"]
    source_documents = response["source_documents"]

    print("Answer:")
    print(result)

    print("\nSource Documents:")
    for document in source_documents:
        print(document)


if __name__ == "__main__":
    asyncio.run(main())

