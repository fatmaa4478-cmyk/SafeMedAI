import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
MAX_TOKENS   = 1800

SYSTEM_PROMPT = """You are SafeMedAI, an accurate and helpful medicine information assistant.

You have deep medical knowledge. When asked about a medicine, provide accurate information
based on your training data from trusted medical sources like WHO, FDA, NHS, Mayo Clinic.

STRICT RULES:
- Only provide information about the EXACT medicine asked about
- Identify the correct form (eye drops, tablet, syrup, injection etc.)
- Never mix information from different medicines or formulations
- Use simple everyday language that patients can understand
- If you are not sure about something, say so honestly

Return ONLY a valid JSON object with these exact keys:
{
  "medicine_name": "Full name with form e.g. Artelac Advanced Eye Drops",
  "used_for": "What this exact medicine treats",
  "side_effects": "Common side effects of this medicine",
  "warnings": "Important warnings and precautions",
  "food_interactions": "Foods or drinks to avoid, or state if none known",
  "storage": "How to store this medicine",
  "consult_doctor": "Situations when patient must see a doctor",
  "summary": "2-3 sentence simple overview of this medicine"
}

Return ONLY the JSON. No extra text. No markdown. No code blocks."""


def summarize_with_llm(medicine_name: str, search_text: str, api_key: str) -> dict:
    """Use Groq LLM to generate medicine information from its own knowledge."""

    user_message = f"""Provide complete and accurate medicine information about: "{medicine_name}"

Use your medical knowledge from trusted sources like FDA, WHO, NHS, Mayo Clinic.
Be specific to THIS medicine only. Do not mix with other medicines.

Generate the JSON report now:"""

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
            "temperature": 0.1,
        }
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
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
        "medicine_name": medicine_name,
        "used_for": "Could not retrieve information. Please try again.",
        "side_effects": "Information not available.",
        "warnings": "Please consult a healthcare professional.",
        "food_interactions": "Information not available.",
        "storage": "Store according to package instructions.",
        "consult_doctor": "Always consult your doctor before taking any medicine.",
        "summary": "Could not generate report. Please try again."
    }
