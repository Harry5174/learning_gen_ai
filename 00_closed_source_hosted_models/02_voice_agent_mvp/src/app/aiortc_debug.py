#!/usr/bin/env python3
import os
import sys
import time
import json
import base64
import struct
import wave

import requests
import soundfile as sf


from websocket import create_connection, WebSocketConnectionClosedException

# ─── 1. Obtain ephemeral key ─────────────────────────────────────────────────
def create_ephemeral_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the OPENAI_API_KEY environment variable")
    resp = requests.post(
        "https://api.openai.com/v1/realtime/sessions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "openai-beta": "realtime=v1"
        },
        json={
            "model": "gpt-4o-realtime-preview-2025-06-03",
            "voice": "alloy"
        },
    )
    resp.raise_for_status()
    return resp.json()["client_secret"]["value"]

# ─── 2. Audio conversion helpers ─────────────────────────────────────────────
def float_to_pcm16(arr):
    clipped = [max(-1.0, min(1.0, x)) for x in arr]
    return b"".join(struct.pack("<h", int(x * 32767)) for x in clipped)

def pcm16_to_b64(pcm_bytes):
    return base64.b64encode(pcm_bytes).decode("ascii")

# ─── 3. Main: stream WAV, commit, request response, save output ─────────────
def main(wav_path):
    # 3.1 Create ephemeral key
    secret = create_ephemeral_key()

    # 3.2 Open WebSocket
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2025-06-03"
    headers = [
        f"Authorization: Bearer {secret}",
        "openai-beta: realtime=v1"
    ]
    ws = create_connection(url, header=headers)

    # 3.3 Wait for session.created
    greeting = ws.recv()
    print("←", greeting)

    # 3.4 Read input WAV (float32 PCM)
    data, sr = sf.read(wav_path, dtype="float32")
    channel = data[:, 0] if data.ndim > 1 else data
    chunk_size = int(0.2 * sr)  # 0.2s per chunk

    # 3.5 Stream audio chunks in real time
    for i in range(0, len(channel), chunk_size):
        block = channel[i : i + chunk_size]
        pcm = float_to_pcm16(block)
        b64 = pcm16_to_b64(pcm)
        ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": b64
        }))
        time.sleep(len(block) / sr)

    # 3.6 Signal end-of-input
    ws.send(json.dumps({
        "type": "input_audio_buffer.append",
        "audio": "",
        "last": True
    }))

    # 3.7 Commit the audio as a user message
    ws.send(json.dumps({
        "type": "input_audio_buffer.commit"
    }))

    # 3.8 Ask the model to respond (both audio & text)
    ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "modalities": ["audio", "text"]
        }
    }))

    # 3.9 Prepare to collect the assistant’s PCM16 audio
    pcm_buffer = bytearray()

    # ─── 4. Receive loop: collect audio + final transcript ────────────────────
    while True:
        try:
            msg = ws.recv()
        except WebSocketConnectionClosedException:
            print("Connection closed by server.")
            break

        if not msg or not isinstance(msg, str):
            continue

        try:
            evt = json.loads(msg)
        except json.JSONDecodeError:
            continue

        t = evt.get("type", "")
        if t == "response.audio.delta":
            pcm_buffer.extend(base64.b64decode(evt["delta"]))

        elif t == "response.done":
            # 4.1 Write the collected PCM16 to response.wav at 24 kHz
            with wave.open("response.wav", "wb") as wf:
                wf.setnchannels(1)      # mono
                wf.setsampwidth(2)      # 16-bit
                wf.setframerate(24000)  # <— match API’s output rate
                wf.writeframes(pcm_buffer)
            print("→ Saved assistant audio to response.wav")

            # 4.2 Print the transcript
            assistant_item = evt["response"]["output"][0]
            transcript = assistant_item["content"][0]["transcript"]
            print("→ Assistant said:", transcript)
            break

    ws.close()

# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python aiortc_debug.py <input.wav>")
        sys.exit(1)
    main(sys.argv[1])
