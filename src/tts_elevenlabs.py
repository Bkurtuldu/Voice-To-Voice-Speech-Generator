import requests

def tts_to_pcm16(text: str, api_key: str, voice_id: str, model_id: str = "eleven_multilingual_v2", pcm_rate: int = 16000):
    params = {"output_format": f"pcm_{pcm_rate}"}
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/octet-stream",
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": model_id,
    }
    resp = requests.post(url, params=params, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    audio_bytes = resp.content
    return audio_bytes, pcm_rate