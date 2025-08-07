from fastapi import FastAPI, logger
from app.routes.webscrap_routes import router as webscrap_routes
from app.routes.webscrap_routes import scrape_and_create_pdfs
from app.rag_chatbot_pipeline.interaction_handler.chat_operations import question_answer
from contextlib import asynccontextmanager
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Initialize FastAPI app
app = FastAPI(title="RAG chat application", version="0.1.0")
# Initialize scheduler
scheduler = AsyncIOScheduler()

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting scheduler")
    scheduler.start()
    yield
    logging.info("Stopping scheduler")
    scheduler.shutdown()

# Update FastAPI app with lifespan
app = FastAPI(
    title="RAG chat application", 
    version="0.1.0",
    lifespan=lifespan, 
)

# Your scheduled task (no changes here)
async def scheduled_task():
    urls = [
        #urls you want to schedule
    ]
    await scrape_and_create_pdfs(urls)

# Add job to scheduler 
scheduler.add_job(scheduled_task, 'interval', weeks=1) 

# Include your routers
app.include_router(webscrap_routes,prefix="/webscrap")

@app.get('/')
def read_root():
    return {'Message': 'This is a RAG-architecture based AI application-backend'}

from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str


@app.post('/chat')
async def read_chat(request: ChatRequest):
    try:
        req: str = request.query
        print(req)
        response = await question_answer(query=req)

        if response:
            chat_result = response['result']
            source_documents = response['source_documents']

            return {"chat_result": chat_result, "source_documents": source_documents}
        else:
            return {"message": "No results found!"}
        
    except Exception as e:
        logger.exception("Error in chat retrieval:")  
        return {"message": "An error occurred while retrieving the chat."} 