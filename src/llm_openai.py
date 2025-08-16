import os
from openai import OpenAI

def generate_reply_tr(user_text: str, model: str = "gpt-4.1-mini") -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "Türkçe konuş. Cevapların kısa ve net olsun. Maksimum 2-3 cümle."
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt},{"role": "user", "content": user_text}],
        temperature=0.3,
        max_tokens=200,
    )
    return (resp.choices[0].message.content or "").strip()