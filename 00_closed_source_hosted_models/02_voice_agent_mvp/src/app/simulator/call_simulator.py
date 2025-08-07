"""
Simulates a SIP call by streaming an input WAV file (any sample rate) as µ-law RTP via HTTP POST
chunks to the /audio endpoint, then sends a BYE event to trigger the call tear-down.
"""
import sys
import time
import requests
import audioop
import soundfile as sf

BASE_URL = "http://127.0.0.1:8000"
AUDIO_ENDPOINT = f"{BASE_URL}/audio"
SIP_EVENT_ENDPOINT = f"{BASE_URL}/sip_event"
CHUNK_MS = 20  # milliseconds per audio chunk


def send_wav_as_audio_endpoint(wav_path: str, call_id: str) -> None:
    # Read arbitrary WAV into int16 PCM
    data, sr = sf.read(wav_path, dtype='int16')
    # Convert to mono if needed
    if data.ndim > 1:
        data = data[:, 0]
    pcm_bytes = data.tobytes()

    # Resample to 8kHz if necessary
    if sr != 8000:
        pcm_bytes, _ = audioop.ratecv(pcm_bytes, 2, 1, sr, 8000, None)
        sr = 8000

    # Calculate chunk sizes
    frames_per_chunk = int(sr * (CHUNK_MS / 1000.0))
    bytes_per_chunk = frames_per_chunk * 2  # 2 bytes per sample
    total_chunks = (len(pcm_bytes) + bytes_per_chunk - 1) // bytes_per_chunk

    print(f"Streaming {total_chunks} chunks of {bytes_per_chunk} bytes to {AUDIO_ENDPOINT}")

    for idx in range(total_chunks):
        start = idx * bytes_per_chunk
        end = start + bytes_per_chunk
        chunk = pcm_bytes[start:end]
        # Convert PCM16 to PCMU (µ-law)
        pcmu = audioop.lin2ulaw(chunk, 2)

        # POST to /audio with multipart/form-data
        files = {
            'audio': ('chunk.pcmu', pcmu, 'application/octet-stream')
        }
        data = {
            'call_id': call_id
        }
        resp = requests.post(AUDIO_ENDPOINT, data=data, files=files)
        if resp.status_code != 200:
            print(f"Error sending chunk {idx}/{total_chunks-1}: {resp.status_code} {resp.text}")
            break
        print(f"Chunk {idx:03d}/{total_chunks-1:03d} sent, {len(pcmu)} bytes")
        time.sleep(CHUNK_MS / 1000.0)

    # Signal end-of-call to trigger tear-down
    print("All chunks sent. Sending BYE to terminate the call.")
    bye_payload = {
        'type': 'BYE',
        'call_id': call_id
    }
    bye_resp = requests.post(SIP_EVENT_ENDPOINT, json=bye_payload)
    if bye_resp.status_code == 200:
        print(f"BYE sent for call_id {call_id}")
    else:
        print(f"Error sending BYE: {bye_resp.status_code} {bye_resp.text}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python call_simulator.py <wav_path> <call_id>")
        sys.exit(1)
    wav_path = sys.argv[1]
    call_id = sys.argv[2]

    # Start by posting INVITE
    invite_payload = {
        'type': 'INVITE',
        'call_id': call_id,
        'from_number': 'simulator',
        'rtp_ip': '127.0.0.1',
        'rtp_port': 5555
    }
    resp = requests.post(SIP_EVENT_ENDPOINT, json=invite_payload)
    if resp.status_code == 200:
        print(f"INVITE sent for call_id {call_id}")
    else:
        print(f"Error sending INVITE: {resp.status_code} {resp.text}")
        return

    # Stream audio
    send_wav_as_audio_endpoint(wav_path, call_id)


if __name__ == '__main__':
    main()
