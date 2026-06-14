import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


def translate_text(text: str, target_language: str = "EN"):
    try:
        if not DEEPL_API_KEY:
            return text, "UNKNOWN"

        response = requests.post(
            DEEPL_URL,
            headers={
                "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "text": [text],
                "target_lang": target_language
                # ❌ DO NOT include source_lang
            },
            timeout=10
        )

        data = response.json()

        translated = data["translations"][0]["text"]
        detected = data["translations"][0].get("detected_source_language", "UNKNOWN")

        return translated, detected

    except Exception as e:
        print("DeepL error:", e)
        return text, "ERROR"