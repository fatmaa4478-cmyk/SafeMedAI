import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


def translate_to_urdu(report: dict, api_key: str) -> dict:
    """Translate the medicine report from English to Urdu."""
    if not report or not api_key:
        print("[Translation] Missing report or API key")
        return None

    # Build a simple string version for translation
    report_str = json.dumps(report, ensure_ascii=False, indent=2)

    system_prompt = """You are a professional Urdu medical translator.
Translate the given JSON medicine report from English to Urdu.
Use simple everyday Urdu that Pakistani patients can understand.
Keep medicine names in English (do not translate medicine names).
Return ONLY a valid JSON object with the exact same keys but Urdu translated values.
No extra text. No markdown. Just the JSON."""

    user_message = f"""Translate all values in this JSON to Urdu. Keep the keys in English. Keep medicine names in English.

{report_str}

Return the translated JSON now:"""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            "max_tokens": 2000,
            "temperature": 0.1,
        }

        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=40
        )
        response.raise_for_status()

        ai_text = response.json()["choices"][0]["message"]["content"].strip()
        print(f"[Translation] Raw response: {ai_text[:200]}")

        # Try direct JSON parse
        try:
            return json.loads(ai_text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from response
        start = ai_text.find("{")
        end   = ai_text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(ai_text[start:end])

        print("[Translation] Could not parse JSON from response")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"[Translation HTTP Error] {response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"[Translation Error] {e}")
        return None
