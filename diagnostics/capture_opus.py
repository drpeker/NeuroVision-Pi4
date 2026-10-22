import asyncio
import json
import struct
import time
from pathlib import Path

from src.core.protocol_manager import ProtocolTransport

original = ProtocolTransport._enqueue_audio
capture_dir = Path("/tmp/neurovision-opus")
capture_dir.mkdir(exist_ok=True)

audio_file = open(capture_dir / "audio.opuspack", "wb")
timing_file = open(capture_dir / "timing.jsonl", "w")

packet_count = 0
start = time.monotonic()

def capture(self, data: bytes):
    global packet_count

    now = time.monotonic()
    packet_count += 1

    audio_file.write(struct.pack("<I", len(data)))
    audio_file.write(data)
    audio_file.flush()

    timing_file.write(json.dumps({
        "packet": packet_count,
        "time": round(now - start, 6),
        "bytes": len(data),
        "queue_size": self._audio_queue.qsize(),
    }) + "\n")
    timing_file.flush()

    return original(self, data)

ProtocolTransport._enqueue_audio = capture

print("Opus kayıt sistemi hazır.")
print("Kayıt klasörü:", capture_dir)
print("NeuroVision'ı bu Python oturumunda başlatmak için sonraki adım gerekli.")
