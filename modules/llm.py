
import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
MAX_TOKENS   = 1800

SYSTEM_PROMPT = """You are SafeMedAI, a helpful medicine information assistant.
Summarize medicine info from web search results into a clear, easy-to-understand report.
Use simple language. If info is missing, write: Information not available in current sources.
Return ONLY a valid JSON object with these exact keys:
{
  "medicine_name": "string",
  "used_for": "string",
  "side_effects": "string",
  "warnings": "string",
  "food_interactions": "string",
  "storage": "string",
  "consult_doctor": "string",
  "summary": "string"
}
No extra text. No markdown. Just the JSON object."""


def summarize_with_llm(medicine_name: str, search_text: str, api_key: str) -> dict:
    """Send search results to Groq LLM and get a structured medicine report."""
    user_message = f"""Analyze search results about "{medicine_name}" and create a structured JSON report.

SEARCH RESULTS:
{search_text[:6000]}

Generate the JSON report now:"""
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0.2,
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        ai_text = response.json()["choices"][0]["message"]["content"].strip()
        return _parse_llm_response(ai_text)
    except requests.exceptions.HTTPError as e:
        print(f"[LLM HTTP Error] {response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"[LLM Error] {e}")
        return None


def _parse_llm_response(ai_text: str) -> dict:
    """Parse JSON from the LLM response, handling edge cases."""
    try:
        return json.loads(ai_text)
    except json.JSONDecodeError:
        pass
    try:
        start = ai_text.find("{")
        end   = ai_text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(ai_text[start:end])
    except Exception:
        pass
    return {
        "medicine_name": "Unknown",
        "used_for": ai_text[:500] if ai_text else "Could not parse information.",
        "side_effects": "Information not available.",
        "warnings": "Please consult a healthcare professional.",
        "food_interactions": "Information not available.",
        "storage": "Store according to package instructions.",
        "consult_doctor": "Always consult your doctor before taking any medicine.",
        "summary": "We found some information but had trouble formatting it. Please try again."
    }
