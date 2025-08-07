from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.sip.sip_events import SIPEvent                 # Pydantic model
from app.sip.sip_proxy  import sip_proxy                # singleton
from app.audio.audio_ingest import audio_router         # optional – keep if useful

app = FastAPI()

# ───────────────────────────────────────────────────────────────────────────────
#  SIP EVENT HOOK  (INVITE / BYE  via HTTP POST)
# ───────────────────────────────────────────────────────────────────────────────
@app.post("/sip_event")
async def sip_event(event: SIPEvent):
    """
    Asterisk (or the simulator) calls this for INVITE / BYE.
    """
    await sip_proxy.handle_sip_event(event.dict())
    return {"status": "ok", "call_id": event.call_id}

# ───────────────────────────────────────────────────────────────────────────────
#  NEW: WebSocket  /ws   for AudioFork
#     AudioFork dials:  ws://HOST:PORT/ws?rtp_ip=IP&rtp_port=PORT&call_id=ID
# ───────────────────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def ingest_ws(ws: WebSocket):
    """
    Receives u-law 20-ms chunks from Asterisk's AudioFork and feeds them
    straight into sip_proxy.receive_audio().
    """
    params   = ws.query_params
    call_id  = params.get("call_id")
    rtp_ip   = params.get("rtp_ip")
    rtp_port = params.get("rtp_port")

    if not (call_id and rtp_ip and rtp_port):
        await ws.close(code=1003)         # unsupported / bad params
        return

    await ws.accept()
    # NB: INVITE may already have created the queue, but AudioFork can arrive first.
    #     Ensure sip_proxy knows this call exists.
    await sip_proxy.handle_sip_event({
        "type":      "INVITE",
        "call_id":   call_id,
        "from_number": params.get("caller", ""),
        "rtp_ip":    rtp_ip,
        "rtp_port":  int(rtp_port),
    })

    try:
        while True:
            data = await ws.receive_bytes()            # 160‑byte µ‑law
            await sip_proxy.receive_audio(call_id, data)
    except WebSocketDisconnect:
        pass
    finally:
        # graceful BYE if WebSocket disappears before explicit curl BYE
        await sip_proxy.handle_sip_event({"type": "BYE", "call_id": call_id})

# ───────────────────────────────────────────────────────────────────────────────
#  OPTIONAL: keep the old /audio HTTP route for the local simulator
# ───────────────────────────────────────────────────────────────────────────────
app.include_router(audio_router)

@app.get("/")
async def health():
    return {"status": "running"}
