from fastapi import FastAPI, HTTPException
from app.rag_chatbot_pipeline.interaction_handler.chat_operations import question_answer
from app.rag_chatbot_pipeline.data_handler.data_operations import initialize_vector_database, load_documents
from app.schema.models import ChatRequest
from PyPDF2 import PdfReader
import os
import logging

# Logger configuration
Logger = logging.getLogger("chatbot")
Logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
Logger.addHandler(handler)

app = FastAPI(title="RAG chat application", version="0.1.0")
vector_database = None

@app.on_event("startup")
async def startup_event():
    global vector_database
    print("Initializing vector database...")
    vector_database = await load_and_initialize_vector_database()
    if vector_database is None:
        print("Failed to initialize vector database at startup.")
    else:
        print("Vector database initialized successfully.")

async def load_and_initialize_vector_database():
    global vector_database
    if vector_database is None:
        vector_database = await initialize_vector_database()
        if vector_database is None:
            print("Vector database initialization failed!")
        else:
            print(f"Vector database initialized: {type(vector_database)}")
    return vector_database

@app.get('/')
def read_root():
    return {'Message': 'This is a RAG-architecture based AI application-server'}

@app.post('/chat')
async def read_chat(request: ChatRequest):
    try:
        req: str = request.query
        print(dict({"user_query": req}))
        response = await question_answer(query=req)

        if response:
            chat_result = response['result']
            source_documents = response['source_documents']
            return {"chat_result": chat_result, "source_documents": source_documents}
        else:
            return {"message": "No results found!"}
        
    except Exception as e:
        Logger.exception("Error in chat retrieval: %s", str(e))  
        return {"message": "An error occurred while retrieving the chat."}
