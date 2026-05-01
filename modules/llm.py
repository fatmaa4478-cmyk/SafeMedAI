import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
MAX_TOKENS   = 1800

SYSTEM_PROMPT = """You are SafeMedAI, a careful and accurate medicine information assistant.
Your job is to summarize medicine information ONLY about the EXACT medicine the user asked about.

STRICT RULES:
- Only include information specifically about the exact medicine named by the user
- Do NOT mix information from other medicines with similar ingredients
- Do NOT include uses, side effects, or warnings from different formulations or products
- If a piece of information seems unrelated to the exact medicine, exclude it
- Use simple everyday language
- If information for a section is not found, write exactly: "Information not available in current sources."
- Never recommend specific dosages

You MUST return ONLY a valid JSON object with these exact keys:
{
  "medicine_name": "Official name of the exact medicine asked about",
  "used_for": "What THIS specific medicine treats",
  "side_effects": "Side effects of THIS specific medicine only",
  "warnings": "Warnings for THIS specific medicine only",
  "food_interactions": "Food or drink interactions for THIS specific medicine",
  "storage": "Storage instructions for THIS specific medicine",
  "consult_doctor": "When to see a doctor regarding THIS specific medicine",
  "summary": "2-3 sentence plain English overview of THIS specific medicine only"
}

Return ONLY the JSON. No extra text. No markdown. No code blocks."""


def summarize_with_llm(medicine_name: str, search_text: str, api_key: str) -> dict:
    """Send search results to Groq LLM and get a structured medicine report."""
    user_message = f"""The user is asking about this EXACT medicine: "{medicine_name}"

IMPORTANT: Only provide information about "{medicine_name}" specifically.
Do NOT mix in information about other medicines, even if they share ingredients.

Here are the search results to analyze:
{search_text[:6000]}

Now generate the JSON report ONLY about "{medicine_name}":"""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0.1,  # Very low = more accurate, less creative
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
    """Parse JSON from the LLM response."""
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
        "used_for": "Could not parse information.",
        "side_effects": "Information not available.",
        "warnings": "Please consult a healthcare professional.",
        "food_interactions": "Information not available.",
        "storage": "Store according to package instructions.",
        "consult_doctor": "Always consult your doctor before taking any medicine.",
        "summary": "We found some information but had trouble formatting it. Please try again."
    }
