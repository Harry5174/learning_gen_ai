from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from langchain.llms import Ollama

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from app.rag_chatbot_pipeline.data_handler.data_operations import initialize_vector_database

from app.llm.openai_connectivity import OPENAI_API_KEY

vector_database = None

async def load_and_initialize_vector_database():
    global vector_database
    if not vector_database:
        # Await the initialization if it's an async function
        vector_database = await initialize_vector_database()
        
        if vector_database is None:
            print("Vector database initialization failed!")
        else:
            if hasattr(vector_database, 'as_retriever'):
                print("Vector database has as_retriever method")
            else:
                print("Error: vector_database does not have as_retriever method")

            print(f"Vector database initialized: {type(vector_database)}")

async def question_answer(query: str):
    # Ensure vector database is initialized before running the QA
    await load_and_initialize_vector_database()

    # Define the prompt template
    template = """You are Scout's assistant chatbot. Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Greet properly in response to a greet.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # Define the retrieval QA chain using OpenAI's GPT-4
    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=OPENAI_API_KEY),
        chain_type="stuff",
        retriever=vector_database.as_retriever(),  # Use the retriever
        chain_type_kwargs={'prompt': QA_CHAIN_PROMPT},
        return_source_documents=True,
        verbose=True
    )

    # Asynchronously call the QA chain using ainvoke
    response = await qa.ainvoke({"query": query})
    
    # Extract the result and source documents
    result = response.get("result")
    source_documents = response.get("source_documents", [])
    
    return {"result": result, "source_documents": source_documents}

async def question_answer_using_mistral(query: str):
    # Ensure vector database is initialized before running the QA
    await load_and_initialize_vector_database()

    # Define the prompt template
    template = """You are Scout's assistant chatbot. Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Greet properly in response to a greet.
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # Define the custom LLM with Mistral (via Ollama)
    mistral_llm = Ollama(
        base_url="http://localhost:11434", 
        model="mistral", 
        verbose=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    )

    # Define the retrieval QA chain using the custom Mistral LLM
    qa = RetrievalQA.from_chain_type(
        llm=mistral_llm,  # Use the Mistral LLM instead of GPT-4
        chain_type="stuff",
        retriever=vector_database.as_retriever(),  # Use the retriever
        chain_type_kwargs={'prompt': QA_CHAIN_PROMPT},
        return_source_documents=True,
        verbose=True
    )

    # Asynchronously call the QA chain using ainvoke
    response = await qa.ainvoke({"query": query})

    # Extract the result and source documents
    result = response.get("result")
    source_documents = response.get("source_documents", [])

    return {"result": result, "source_documents": source_documents}
