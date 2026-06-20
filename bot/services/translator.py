import os
import requests

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# -----------------------------
# TRANSLATION FUNCTION
# -----------------------------
def translate_text(text: str, target_lang: str):
    """
    Translate text using DeepL API.

    Returns:
        translated_text (str)
        detected_language (str)
    """

    if not DEEPL_API_KEY:
        raise RuntimeError("DEEPL_API_KEY is missing.")

    url = "https://api-free.deepl.com/v2/translate"

    payload = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang
    }

    response = requests.post(url, data=payload)
    data = response.json()

    # Safety check (prevents crashes if API fails)
    if "translations" not in data:
        raise RuntimeError(f"DeepL API error: {data}")

    translated = data["translations"][0]["text"]
    detected = data["translations"][0].get("detected_source_language", "unknown")

    return translated, detected