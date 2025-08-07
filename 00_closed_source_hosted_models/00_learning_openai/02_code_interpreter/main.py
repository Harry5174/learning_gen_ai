import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
from openai.resources.beta.threads.messages.messages import SyncCursorPage
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from packaging import version
from openai import OpenAI
import functions
import asyncio

load_dotenv()

# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Use .get() to avoid KeyError
if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

app = FastAPI()

# Placeholder types for message content / classes
class ChatRequest(BaseModel):
    thread_id: str  
    message: str

class ChatResponse(BaseModel):
    response: str

# Init OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create new assistant or load existing
assistant_id = functions.create_assistant(client)

# creating new thread
@app.get('/start')
async def start_conversation():
    print("Starting a new conversation...")
    thread = client.beta.threads.create()
    thread_id = thread.id
    print(f"New thread created with ID: {thread_id}")
    return {"thread_id": thread_id}


@app.post('/chat')
async def chat(request: ChatRequest):
    thread_id = request.thread_id
    user_input = request.message
    
    if not thread_id:
        print("Error: Missing thread id")
        return JSONResponse({"Error": "Missing thread id"}), 400

    print(f"recieved message: {user_input} for thread: {thread_id}")

    #adding user message to the thread
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    # #running the assistant
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id= assistant_id, instructions="Please address the user as Jane Doe. The user has a premium account.")

    #check if the run requires action(function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            # dict(run)
            break
        await asyncio.sleep(1)
        
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
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