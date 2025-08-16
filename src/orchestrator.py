import os
import sys
import threading
from dotenv import load_dotenv
import readchar

from src.audio import record_until_event, play_pcm16
from src.stt_deepgram import transcribe_wav
from src.llm_openai import generate_reply_tr
from src.tts_elevenlabs import tts_to_pcm16
from src.logger import JSONLogger

def wait_for_space_or_q():
    while True:
        key = readchar.readkey()
        if key == " ":
            return "space"
        if key.lower() == "q":
            return "quit"


def main():
    load_dotenv()
    LOG_DIR = os.getenv("LOG_DIR", "./data/logs")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    DEEPGRAM_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-2")
    DEEPGRAM_LANGUAGE = os.getenv("DEEPGRAM_LANGUAGE", "tr")
    ELEVEN_MODEL = os.getenv("ELEVEN_MODEL", "eleven_multilingual_v2")

    if not all([DEEPGRAM_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, os.getenv("OPENAI_API_KEY")]):
        print("[ERR] Missing API KEY")
        sys.exit(1)

    logger = JSONLogger(LOG_DIR)

    print("\nVoice Orchestrator running")
    print("Press SPACE to start/stop recording. Press 'q' to quit.\n")

    turn_id = 1
    while True:
        print("[READY] Press SPACE to start recording…")
        action = wait_for_space_or_q()
        if action == "quit":
            print("Bye!")
            break

        print("[REC] Recording… (press SPACE again to stop)")
        stop_event = threading.Event()

        rec_thread = threading.Thread(target=record_until_event, args=(stop_event,), kwargs={"samplerate":16000, "channels":1})
        rec_thread.start()

        action = wait_for_space_or_q()
        stop_event.set()
        rec_thread.join()
        if action == "quit":
            print("[CANCEL] Stopping and exiting…")
            break

        wav_bytes = record_until_event.last_wav_bytes
        if not wav_bytes:
            print("[WARN] No audio captured.")
            continue

        # STT
        try:
            print("[STT] Transcribing with Deepgram…")
            user_text = transcribe_wav(wav_bytes, api_key=DEEPGRAM_API_KEY, model=DEEPGRAM_MODEL, language=DEEPGRAM_LANGUAGE)
            print(f"[USER] {user_text}")
        except Exception as e:
            print(f"[ERR] STT failed: {e}")
            continue

        if not user_text.strip():
            print("[INFO] Empty transcription, skipping.")
            continue

        # LLM
        try:
            print("[LLM] Generating reply (TR)…")
            assistant_text = generate_reply_tr(user_text, model=OPENAI_MODEL)
            print(f"[ASSISTANT] {assistant_text}")
        except Exception as e:
            print(f"[ERR] LLM failed: {e}")
            continue

        # TTS
        try:
            print("[TTS] Synthesizing speech with ElevenLabs…")
            pcm_bytes, pcm_rate = tts_to_pcm16(assistant_text, api_key=ELEVENLABS_API_KEY, voice_id=ELEVENLABS_VOICE_ID, model_id=ELEVEN_MODEL)
        except Exception as e:
            print(f"[ERR] TTS failed: {e}")
            continue

        # Playback
        try:
            print("[PLAY] Playing reply…")
            play_pcm16(pcm_bytes, samplerate=pcm_rate)
        except Exception as e:
            print(f"[ERR] Playback failed: {e}")

        # Log
        try:
            logger.log_turn(turn_id=turn_id, user_text=user_text, assistant_text=assistant_text)
            turn_id += 1
        except Exception as e:
            print(f"[WARN] Logging failed: {e}")


if __name__ == "__main__":
    main()