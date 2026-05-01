
import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


def translate_to_urdu(report: dict, api_key: str) -> dict:
    """Translate the medicine report dictionary from English to Urdu."""
    if not report or not api_key:
        return None
    system = """You are a professional medical translator.
Translate the given English medicine information JSON into Urdu.
Use simple, everyday Urdu that Pakistani patients can understand.
Return ONLY a valid JSON object with the same keys but Urdu values. No extra text."""
    user = f"Translate this medicine report to Urdu:\n\n{json.dumps(report, ensure_ascii=False, indent=2)}"
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            "max_tokens": 2000,
            "temperature": 0.1,
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        ai_text = response.json()["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(ai_text)
        except json.JSONDecodeError:
            start = ai_text.find("{")
            end   = ai_text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(ai_text[start:end])
    except Exception as e:
        print(f"[Translation Error] {e}")
    return None
