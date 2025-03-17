import json
import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from src.aiou.database.database_connectivity import OPENAI_API_KEY,  create_db_engine
from src.aiou.assistant_creation.creation import create_assistant
from src.aiou.models.pydantic_models import ChatRequest, ChatResponse, api_call_arguments

from ..openai.openai_connectivity import version_check, create_client

version_check()

def show_json(message, obj):
    print(message, json.loads(obj.model_dump_json()))

app = FastAPI()

# Init OpenAI client bys self made function
client = create_client(OPENAI_API_KEY)

# Create new assistant or load existing
assistant_id = create_assistant(client)

# start the conversation by creating a new assistant thread id
@app.get('/start')
async def start_conversation():
    thread = client.beta.threads.create()
    thread_id = thread.id
    print({"thread_id": thread_id})
    return {"thread_id": thread_id}

@app.get('/') 
def hello_world():
    return {"message": "This is aiou's assistant backend!"}

# start the conversation using assistant via ('/chat') api endpoint
@app.post('/chat')
async def chat(request: ChatRequest):
    thread_id:str = request.thread_id
    user_input: str = request.message
    
    if not thread_id:
        print("Error: Missing thread id")
        return JSONResponse({"Error": "Missing thread id"}), 400

    print(f"recieved message: {user_input} for thread: {thread_id}")

    #adding user message to the thread
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    # #running the assistant
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id= assistant_id)

    # check run_status
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            break
        await asyncio.sleep(1)
        
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    #parsing the messages
    if messages.data[0].content:
        message_content = messages.data[0].content[0]
        if hasattr(message_content, 'text'):
            response = message_content.text.value
            print(response)
        elif hasattr(message_content, 'image_file'):
            #To Handle the case where it's an image file
            print("Received an image message.")
        else:
            # Fallback for unrecognized types
            print("Received an unrecognized type of message.")
        return JSONResponse({"response": response})
    else:
        print("The latest message has no content.")
        return JSONResponse({"Error": "The latest message has no content"}, status_code=404)
    