from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    thread_id: str  
    message: str

class ChatResponse(BaseModel):
    response: str

class api_call_arguments(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None