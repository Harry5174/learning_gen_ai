import os
import json
import base64
import asyncio
import logging
from typing import AsyncIterable, AsyncGenerator
import aiohttp  
from app.config import OPENAI_API_KEY

# logger
tx_logger = logging.getLogger("openai_ws_bridge")
tx_logger.setLevel(logging.INFO)

async def fetch_ephemeral_key() -> str:
    """
    Create a new OpenAI realtime session and return its client_secret asynchronously.
    """
    url = "https://api.openai.com/v1/realtime/sessions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "openai-beta": "realtime=v1",
    }
    payload = {
        "model": "gpt-4o-realtime-preview-2025-06-03",
        "voice": "shimmer",
        "instructions": "You are a helpful assistant in a call center. Respond clearly and concisely in English."
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()

    key = data.get("client_secret", {}).get("value")
    if not key:
        raise RuntimeError("Failed to fetch ephemeral key from OpenAI")
    tx_logger.info("Obtained ephemeral key")
    return key

async def openai_stream(
    audio_chunks: AsyncIterable[bytes]
) -> AsyncGenerator[bytes, None]:
    """
    Async generator that streams PCM16@16k audio to OpenAI in real time
    and yields PCM16@24k TTS deltas as they arrive.
    """
    key = await fetch_ephemeral_key()
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2025-06-03"
    headers = {
        "Authorization": f"Bearer {key}",
        "openai-beta": "realtime=v1",
    }

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url, headers=headers) as ws:
            # Receive greeting
            msg = await ws.receive()
            tx_logger.info(f"WebSocket greeting: {msg.data[:80]}")

            # Send initial response.create
            await ws.send_json({
                "type": "response.create",
                "response": {"modalities": ["audio", "text"]},
            })

            async def send_loop():
                async for pcm16 in audio_chunks:
                    await ws.send_json({
                        "type": "input_audio_buffer.append",
                        "audio": base64.b64encode(pcm16).decode('ascii'),
                    })
                # End-of-stream
                await ws.send_json({"type": "input_audio_buffer.append", "audio": "", "last": True})
                await ws.send_json({"type": "input_audio_buffer.commit"})

            async def recv_loop():
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        evt = json.loads(msg.data)
                        t = evt.get("type")
                        if t == "response.audio.delta":
                            delta = evt.get("delta", "")
                            if delta:
                                yield base64.b64decode(delta)
                        elif t == "response.done":
                            tx_logger.info("Received response.done")
                            return
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        break

            send_task = asyncio.create_task(send_loop())
            async for pcm24_chunk in recv_loop():
                yield pcm24_chunk
            await send_task
            tx_logger.info("openai_stream completed")
