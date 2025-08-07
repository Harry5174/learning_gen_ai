import os
import json
import httpx
import asyncio
import functions

import openai
from openai.types.beta.threads.run import Run

from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import URL
from sqlmodel import SQLModel, Field, Session, create_engine, select

from packaging import version
from typing import Annotated, Optional

# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
#check version compatibility
if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Use getenv to avoid KeyError if variable is not set
database_url: Optional[str | URL] = os.getenv("database_url") # insert your database url here

# Database model for logging queries and responses
class QueryLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_query: str
    assistant_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Location(SQLModel, table=True):
    name: str = Field(index=True, primary_key=True)
    location: str

# Database setup

# Ensure database_url is not None before passing it to create_engine
if database_url is not None:
    engine = create_engine(database_url)
else:
    raise ValueError("DATABASE_URL environment variable is not set")

# function for creating the QueryLog and Location tables in database if not created
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# @asynccontextmanager / create_db_and_tables
def lifespan(app: FastAPI):
    create_db_and_tables()

def show_json(message, obj):
    print(message, json.loads(obj.model_dump_json()))

app = FastAPI()

# Placeholder types for message content using pydantic
class ChatRequest(BaseModel):
    thread_id: str  
    message: str

class ChatResponse(BaseModel):
    response: str

class api_call_arguments(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

# Init OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Create new assistant or load existing
assistant_id = functions.create_assistant(client)

# start the conversation by creating a new assistant thread id
@app.get('/start')
async def start_conversation():
    thread = client.beta.threads.create()
    thread_id = thread.id
    print({"thread_id": thread_id})
    return {"thread_id": thread_id}

#  functions which will communicate with database incorporated within fastapi endpoints
@app.get("/persons/")
def read_all_persons():
    """
    Retrieves all persons from the database.

    Returns:
        list: A list of Location objects representing the persons.
    """
    with Session(engine) as session:
        loc_data = session.exec(select(Location)).all()
        return loc_data

@app.post("/person/")
def create_person(person_data: Location):
    """
    Creates a new person record in the database.

    Args:
        person_data (Location): name and location of person. 

    Returns:
        Location: The created person record that is name and location of person. 
    """
    with Session(engine) as session:
        session.add(person_data)
        session.commit()
        session.refresh(person_data)
        return person_data

# dependency injection function
def get_location_or_404(name:str)->Location:
    with Session(engine) as session:
        loc_data = session.exec(select(Location).where(Location.name == name)).first()
        if not loc_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No location found for {name}")
        return loc_data

@app.get("/location/{name}")
def get_person_location(name: str, location: Annotated[Location, Depends(get_location_or_404)]):
    """
    Retrieve the location of a person by their name.

    Args:
        name (str): The name of the person.

    Returns:
        Location: The location of the person.
    """
    print(f"Fetching location for {name}")
    
    print(f"Retrieved location data: {location}")
    return location

# start the conversation using assistant via ('/chat') api endpoint
@app.post('/chat')
async def chat(request: ChatRequest):
    thread_id = request.thread_id
    user_input = request.message
    # check for thread_id
    if not thread_id:
        return JSONResponse(content={"Error": "Missing thread id"}, status_code=400)

    # request thread message upon recieving thread_id
    message = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)
    dict(message)

    #run the request to assistant
    run: Run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    dict(run)

    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            break
        elif run_status.status == "requires_action":
            # Handle the required actions by making API calls to your internal endpoints
            print(run_status.required_action)
            tool_outputs = await handle_required_actions(run_status.required_action)
            # Submit tool outputs to continue the run
            client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)
        elif run_status.status in ["failed", "expired"]:
            raise HTTPException(status_code=500, detail="Assistant processing failed or expired")
        else:
            await asyncio.sleep(1)
    
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    if messages.data and messages.data[0].content:
        message_content = messages.data[0].content[0]
        if hasattr(message_content, 'text'):
            response = message_content.text.value
            # Log the query and response in the database
            print(response)
            with Session(engine) as session:
                log_entry = QueryLog(user_query=user_input, assistant_response=response)
                session.add(log_entry)
                session.commit()
            return JSONResponse(content={"response": response})
        else:
            return JSONResponse(content={"Error": "The response format is not recognized"}, status_code=400)
    else:
        return JSONResponse(content={"Error": "The latest message has no content"}, status_code=404)

async def handle_required_actions(required_action):
    tool_outputs = []
    for tool_call in required_action.submit_tool_outputs.tool_calls:
        action_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Make the internal API call based on the action required by the assistant
        response =await make_internal_api_call(action_name, arguments)
        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": json.dumps(response)  # Ensure the output is serialized as a JSON string
        })
    return tool_outputs

from typing import Optional, Dict, Any
import httpx

async def make_internal_api_call(function_name: str, arguments: Optional[Dict[str, Any]] = None):
    try:
        async with httpx.AsyncClient() as client:
            base_url = "http://localhost:8000"

            if function_name == "get_person_location":
                if arguments and "name" in arguments:
                    url = f"{base_url}/location/{arguments['name']}"
                    response = await client.get(url)
                else:
                    return {"error": "Missing required 'name' argument for 'get_person_location'"}

            elif function_name == "read_all_persons":
                url = f"{base_url}/persons/"
                response = await client.get(url)

            elif function_name == "create_person":
                if arguments and "name" in arguments and "location" in arguments:
                    url = f"{base_url}/person/"
                    # Passing the dictionary directly as JSON
                    response = await client.post(url, json={"name": arguments["name"], "location": arguments["location"]})
                else:
                    return {"error": "Missing required arguments for 'create_person'"}

            else:
                return {"error": "Unsupported action"}

            try:
                return response.json()
            except ValueError:  # Includes simplejson.errors.JSONDecodeError
                return {"error": "Failed to decode JSON response"}
    except httpx.ReadTimeout:
        # Handle the ReadTimeout exception here
        return {"error": "ReadTimeout occurred while making the internal API call"}