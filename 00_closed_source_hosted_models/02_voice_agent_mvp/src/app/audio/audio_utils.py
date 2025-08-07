import audioop

def pcmu_to_pcm16(pcmu_bytes: bytes) -> bytes:
    """Convert μ-law (PCMU, 8kHz) to PCM16 (8kHz)"""
    return audioop.ulaw2lin(pcmu_bytes, 2)

def pcm16_8k_to_16k(pcm_8k_bytes: bytes) -> bytes:
    """Resample PCM16 8kHz mono to 16kHz mono"""
    return audioop.ratecv(pcm_8k_bytes, 2, 1, 8000, 16000, None)[0]
