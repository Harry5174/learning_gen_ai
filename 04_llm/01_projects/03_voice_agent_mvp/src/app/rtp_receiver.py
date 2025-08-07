import socket, audioop, wave, sys

if len(sys.argv) != 2:
    print("Usage: python rtp_receiver.py <port>")
    sys.exit(1)

port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", port))
print(f"Listening for RTP on UDP port {port}…")

# collect raw µ-law payloads
ulaw_buf = bytearray()
try:
    while True:
        packet, addr = sock.recvfrom(2048)
        # strip 12-byte RTP header
        payload = packet[12:]
        ulaw_buf.extend(payload)
except KeyboardInterrupt:
    print("Interrupted, saving…")

# convert µ-law → PCM16 @8kHz
pcm16 = audioop.ulaw2lin(bytes(ulaw_buf), 2)
# save to WAV
wav = wave.open("ai_response.wav", "wb")
wav.setnchannels(1)
wav.setsampwidth(2)
wav.setframerate(8000)
wav.writeframes(pcm16)
wav.close()
print("Saved ai_response.wav")
