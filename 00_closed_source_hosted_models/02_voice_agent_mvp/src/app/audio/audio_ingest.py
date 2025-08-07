from fastapi import APIRouter, UploadFile, File, Form
from app.sip.sip_events import active_sessions
from app.sip.sip_proxy import sip_proxy      
import threading

audio_router = APIRouter()
audio_buffers: dict[str, bytearray] = {}
audio_locks: dict[str, threading.Lock] = {}

@audio_router.post("/audio")
async def receive_audio(
    call_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    1) Buffer raw µ-law bytes for debugging (flush_audio)
    2) Enqueue raw µ-law bytes into SIPProxy for OpenAI bridge
    """
    if call_id not in active_sessions:
        return {"status": "error", "msg": f"Unknown call_id {call_id}"}

    audio_bytes = await audio.read()

    # 1) local buffer for debug
    if call_id not in audio_buffers:
        audio_buffers[call_id] = bytearray()
        audio_locks[call_id] = threading.Lock()
    with audio_locks[call_id]:
        audio_buffers[call_id].extend(audio_bytes)

    # 2) forward into SIPProxy
    await sip_proxy.receive_audio(call_id, audio_bytes)

    print(f"Received and forwarded {len(audio_bytes)} bytes for call_id {call_id}")
    return {"status": "ok", "bytes": len(audio_bytes)}

@audio_router.post("/flush_audio")
def flush_audio(call_id: str = Form(...)):
    """
    Manual endpoint to write out the buffered audio to a WAV for inspection.
    """
    import wave, audioop

    if call_id not in audio_buffers:
        return {"status": "error", "msg": "No audio buffer for call_id"}

    with audio_locks[call_id]:
        pcmu = bytes(audio_buffers[call_id])
        pcm16 = audioop.ulaw2lin(pcmu, 2)
        wav_path = f"/tmp/{call_id}_received.wav"
        with wave.open(wav_path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(8000)
            wav.writeframes(pcm16)
        # clean up
        del audio_buffers[call_id]
        del audio_locks[call_id]

    return {"status": "ok", "wav_file": wav_path}

# @audio_router.post("/ws")
# async def ingest_ws(ws: WebSocket):
#     params = ws.query_params
#     call_id = params["call_id"]
#     await ws.accept()
#     while True:
#         try:
#             data = await ws.receive_bytes()
#         except WebSocketDisconnect:
#             break
#         await sip_proxy.receive_audio(call_id, data)