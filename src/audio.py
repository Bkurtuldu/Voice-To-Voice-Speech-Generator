# src/audio.py

import os
import io
import threading
import numpy as np
import sounddevice as sd
import wave

class _State:
    last_wav_bytes: bytes | None = None

state = _State()


def _write_wav_bytes(samplerate: int, channels: int, data_int16: np.ndarray) -> bytes:
    if channels > 1 and data_int16.ndim == 1:
        data_int16 = data_int16.reshape(-1, channels)

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes(data_int16.tobytes())
    return buf.getvalue()


def _pick_device_from_env():
    idx = os.getenv("AUDIODEV_INDEX")
    if idx is not None and idx != "":
        try:
            return int(idx)
        except ValueError:
            return idx
    name = os.getenv("AUDIODEV")
    if name:
        return name
    return None


def record_until_event(stop_event: threading.Event, samplerate: int = 16000, channels: int = 1):

    sr = int(os.getenv("SAMPLERATE", str(samplerate)))
    ch = int(os.getenv("CHANNELS", str(channels)))
    device = _pick_device_from_env()

    print(f"[AUDIO] requested sr={sr} ch={ch} device={device!r}")

    frames: list[np.ndarray] = []

    def callback(indata, frames_count, time_info, status):
        if status:
            print(f"[AUDIO] {status}")
        frames.append((indata.copy() * 32767.0).astype(np.int16))

    try:
        with sd.InputStream(
            device=device,
            samplerate=sr,
            channels=ch,
            dtype='float32',
            callback=callback
        ):
            while not stop_event.is_set():
                sd.sleep(50)
    except Exception as e:
        print("[ERR] InputStream açılamadı:", e)
        record_until_event.last_wav_bytes = None
        return

    if not frames:
        print("[WARN] InputStream çalıştı ama frame gelmedi.")
        record_until_event.last_wav_bytes = None
        return

    audio_i16 = np.concatenate(frames, axis=0)
    wav_bytes = _write_wav_bytes(sr, ch, audio_i16)
    record_until_event.last_wav_bytes = wav_bytes


record_until_event.last_wav_bytes = None


def play_pcm16(pcm_bytes: bytes, samplerate: int = 16000, channels: int = 1):
    arr = np.frombuffer(pcm_bytes, dtype=np.int16)
    if channels > 1:
        arr = arr.reshape(-1, channels)
    audio = arr.astype(np.float32) / 32767.0
    sd.play(audio, samplerate=samplerate)
    sd.wait()