import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


def translate_text(text: str, target_language: str = "EN"):
    """
    Translate text using the DeepL API.

    Returns:
        (translated_text, detected_source_language)
    """

    try:
        if not DEEPL_API_KEY:
            print("ERROR: DEEPL_API_KEY is missing.")
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
            },
            timeout=10
        )

        # Helpful debug output
        print("STATUS:", response.status_code)
        print("RAW RESPONSE:", response.text)

        response.raise_for_status()

        data = response.json()

        translated = data["translations"][0]["text"]
        detected = data["translations"][0].get(
            "detected_source_language",
            "UNKNOWN"
        )

        return translated, detected

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return text, "HTTP_ERROR"

    except requests.exceptions.Timeout:
        print("DeepL request timed out.")
        return text, "TIMEOUT"

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return text, "REQUEST_ERROR"

    except KeyError:
        print("Unexpected response from DeepL:")
        print(response.text)
        return text, "INVALID_RESPONSE"

    except Exception as e:
        print(f"Unexpected error: {e}")
        return text, "ERROR"