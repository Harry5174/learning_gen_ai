import asyncio, wave
from app.openai_ws_bridge import openai_stream

async def main():
    # 1) Load a clear, 3s+ 16 kHz WAV of speech
    wf = wave.open("input.wav", "rb")
    assert wf.getframerate() == 16000 and wf.getnchannels() == 1

    # 2) Async generator of 20 ms frames
    async def gen():
        n = int(0.02 * 16000)
        while True:
            pcm = wf.readframes(n)
            if not pcm:
                break
            yield pcm

    # 3) Run the bridge
    async for pcm24 in openai_stream(gen()):
        print("Received", len(pcm24), "bytes of TTS")
        # write to WAV
        out = wave.open("out_24k.wav","wb")
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(24000)
        out.writeframes(pcm24)
        out.close()

asyncio.run(main())