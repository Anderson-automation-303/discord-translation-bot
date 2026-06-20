import os
import requests

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

DEEPL_URL = "https://api-free.deepl.com/v2/translate"


def translate_text(text: str, target_lang: str):
    """
    DeepL API (NEW header-based auth - 2025 update)
    """

    if not DEEPL_API_KEY:
        raise RuntimeError("DEEPL_API_KEY is missing.")

    headers = {
        "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": [text],
        "target_lang": target_lang
    }

    response = requests.post(
        DEEPL_URL,
        headers=headers,
        json=payload
    )

    data = response.json()

    if "translations" not in data:
        raise RuntimeError(f"DeepL API error: {data}")

    translated = data["translations"][0]["text"]
    detected = data["translations"][0].get("detected_source_language", "unknown")

    return translated, detected