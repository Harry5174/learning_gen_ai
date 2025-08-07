from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict

sip_event_router = APIRouter()

# simple in-memory "active calls" dict for now
active_sessions: Dict[str, dict] = {}

class SIPEvent(BaseModel):
    type: str      # "INVITE" or "BYE"
    call_id: str   # Unique identifier for the call/session
    from_number: str = ""
    rtp_ip: str = ""
    rtp_port: int = 0

@sip_event_router.post("/sip_event")
async def sip_event(event: SIPEvent):
    """
    Simulate SIP call events (INVITE/BYE) for local pipeline testing.
    """
    if event.type == "INVITE":
        active_sessions[event.call_id] = {
            "from_number": event.from_number,
            "rtp_ip": event.rtp_ip,
            "rtp_port": event.rtp_port,
        }
        return {"status": "call started", "call_id": event.call_id}
    elif event.type == "BYE":
        if event.call_id in active_sessions:
            del active_sessions[event.call_id]
            return {"status": "call ended", "call_id": event.call_id}
        else:
            return {"status": "not found", "call_id": event.call_id}
    else:
        return {"status": "unknown event type", "call_id": event.call_id}

# Optionally, an endpoint to view all active sessions (for debug)
@sip_event_router.get("/active_sessions")
async def get_active_sessions():
    return active_sessions


