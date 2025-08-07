import socket

# reuse a single socket for all packets
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
_sock.bind(("0.0.0.0", 0))

# You can also persist per-call seq/timestamp in a dict if needed
_rtp_state = {}

def send_rtp_packet(call_id: str, payload: bytes, ip: str, port: int):
    """
    Send one RTP packet with a minimal header + payload (PCMU payload).
    """
    state = _rtp_state.setdefault(call_id, {
        "seq": 0,
        "ts": 0,
        "ssrc": 1234,  # random or fixed
    })

    hdr = bytearray(12)
    hdr[0], hdr[1] = 0x80, 0x00
    hdr[2:4] = state["seq"].to_bytes(2, "big")
    hdr[4:8] = state["ts"].to_bytes(4, "big")
    hdr[8:12] = state["ssrc"].to_bytes(4, "big")

    packet = hdr + payload
    _sock.sendto(packet, (ip, port))

    # advance sequence and timestamp
    state["seq"] = (state["seq"] + 1) & 0xFFFF
    state["ts"] = (state["ts"] + len(payload)) & 0xFFFFFFFF
