# ── src/app/sip/sip_proxy.py ──────────────────────────────────────────────
import asyncio, contextlib, logging, audioop
from typing import Dict, Optional
from app.openai_ws_bridge import openai_stream
from app.sip.rtp              import send_rtp_packet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PACE_SEC      = 0.02           # one RTP every 20 ms
ULAW_FRAME    = 160            # 160 B µ‑law  = 20 ms @ 8 kHz
TARGET_RMS    = 2500           # simple AGC level

class SIPProxy:
    """
    Singleton: owns per-call queues and paced RTP sender tasks.
    """
    def __init__(self):
        self.audio_q: Dict[str, asyncio.Queue[bytes | None]] = {}
        self.send_task: Dict[str, asyncio.Task]              = {}
        self.active_calls = set()

    # ───────────────────── SIP INVITE / BYE ────────────────────────────
    async def handle_sip_event(self, evt: dict):
        cid      = evt.get("call_id")
        rtp_ip   = evt.get("rtp_ip")
        rtp_port = int(evt.get("rtp_port") or 0)

        t = evt.get("type")
        if t == "INVITE" and cid not in self.active_calls:
            logger.info(f"[SIP {cid}] INVITE")
            q = asyncio.Queue(maxsize=800)          # ≈16 s buffer
            self.audio_q[cid] = q
            self.active_calls.add(cid)
            asyncio.create_task(self._bridge_to_ai(cid, rtp_ip, rtp_port))

        elif t == "BYE":
            logger.info(f"[SIP {cid}] BYE")
            await self._end_call(cid)

    # ───────────────────── AUDIO FROM ASTERISK ─────────────────────────
    async def receive_audio(self, call_id: str, pcmu: bytes):
        if (q := self.audio_q.get(call_id)):
            await q.put(pcmu)

    # ───────────────────── BRIDGE  Caller → GPT‑4o → Caller ────────────
    async def _bridge_to_ai(self, cid: str, ip: str, port: int):
        q_in:  asyncio.Queue = self.audio_q[cid]
        q_out = asyncio.Queue(maxsize=400)          # 8 s of 20 ms frames
        self.send_task[cid] = asyncio.create_task(
            self._rtp_sender(cid, q_out, ip, port)
        )

        # upstream generator  (µ‑law 8 k → PCM‑16 24 k)
        async def pcm24_gen():
            while True:
                ulaw = await q_in.get()
                if ulaw is None:
                    break
                pcm16  = audioop.ulaw2lin(ulaw, 2)
                pcm24, _ = audioop.ratecv(pcm16, 2, 1, 8000, 24000, None)
                yield pcm24

        try:
            # downstream loop  (PCM‑16 48 k → PCM‑16 8 k → µ‑law)
            async for pcm48 in openai_stream(pcm24_gen()):
                pcm8, _ = audioop.ratecv(pcm48, 2, 1, 48000, 8000, None)

                rms  = audioop.rms(pcm8, 2)
                gain = min(TARGET_RMS / max(rms, 1), 4.0)
                pcm8 = audioop.mul(pcm8, 2, gain)

                ulaw = audioop.lin2ulaw(pcm8, 2)
                for i in range(0, len(ulaw), ULAW_FRAME):
                    await q_out.put(ulaw[i : i + ULAW_FRAME])

        except Exception as e:
            logger.exception(f"[AI {cid}] bridge error: {e}")
        finally:
            await q_out.put(None)
            await self.send_task[cid]
            await self._end_call(cid)

    # ───────────────────── PACED RTP SENDER ────────────────────────────
    async def _rtp_sender(self, cid: str, q: asyncio.Queue, ip: str, port: int):
        next_t = asyncio.get_running_loop().time()
        try:
            while True:
                chunk = await q.get()
                if chunk is None:
                    break
                next_t += PACE_SEC
                send_rtp_packet(cid, chunk, ip, port)
                await asyncio.sleep(max(0, next_t - asyncio.get_running_loop().time()))
        except asyncio.CancelledError:
            pass
        finally:
            logger.info(f"[RTPSend {cid}] done")

    # ───────────────────── CLEAN‑UP ────────────────────────────────────
    async def _end_call(self, cid: str):
        if cid in self.active_calls:
            self.active_calls.discard(cid)
        if (q := self.audio_q.pop(cid, None)):
            await q.put(None)
        if (t := self.send_task.pop(cid, None)):
            t.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await t

# singleton
sip_proxy = SIPProxy()
