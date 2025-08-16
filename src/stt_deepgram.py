import requests

def transcribe_wav(wav_bytes: bytes, api_key: str, model: str = "nova-2", language: str = "tr") -> str:
    url = f"https://api.deepgram.com/v1/listen?model={model}&language={language}&punctuate=true"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav",
    }
    resp = requests.post(url, headers=headers, data=wav_bytes, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    try:
        return (
            data.get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
        )
    except Exception:
        return ""