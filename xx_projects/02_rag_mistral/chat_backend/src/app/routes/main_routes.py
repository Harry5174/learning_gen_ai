from fastapi import FastAPI, HTTPException
from app.rag_chatbot_pipeline.interaction_handler.chat_operations import question_answer, question_answer_using_mistral
from app.rag_chatbot_pipeline.data_handler.data_operations import initialize_vector_database
from app.schema.models import ChatRequest
import logging

# Logger configuration
logger = logging.getLogger("chatbot")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI(title="RAG Chat Application", version="0.1.0")
vector_database = None

async def load_and_initialize_vector_database():
    global vector_database
    if vector_database is None:
        vector_database = await initialize_vector_database()
        if vector_database is None:
            logger.error("Vector database initialization failed!")
        else:
            logger.info(f"Vector database initialized: {type(vector_database)}")
    return vector_database

@app.get('/')
def read_root():
    return {'Message': 'This is a RAG-architecture based AI application server'}

@app.post("/chat/openai")
async def chat_with_openai(request: ChatRequest):
    """
    Endpoint to chat with OpenAI's GPT-4 model.
    """
    try:
        req: str = request.query
        logger.debug(f"Received request for OpenAI: {req}")
        
        response = await question_answer(req)

        if response:
            chat_result = response['result']
            source_documents = response['source_documents']
            return {"chat_result": chat_result, "source_documents": source_documents}
        else:   
            logger.warning("No results found for OpenAI query.")
            return {"message": "No results found!"}
        
    except Exception as e:
        logger.exception("Error in chat retrieval with OpenAI: %s", str(e))  
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the chat with OpenAI.")

@app.post("/chat/mistral")
async def chat_with_mistral(request: ChatRequest):
    """
    Endpoint to chat with Mistral 7B model via Ollama.
    """
    try:
        req: str = request.query
        logger.debug(f"Received request for Mistral: {req}")

        # Ensure the vector database is initialized
        await load_and_initialize_vector_database()
        
        response = await question_answer_using_mistral(req)

        if response:
            chat_result = response['result']
            source_documents = response['source_documents']
            return {"chat_result": chat_result, "source_documents": source_documents}
        else:
            logger.warning("No results found for Mistral query.")
            return {"message": "No results found!"}
        
    except Exception as e:
        logger.exception("Error in chat retrieval with Mistral: %s", str(e))  
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the chat with Mistral.")
