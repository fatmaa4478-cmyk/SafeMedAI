import json
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
MAX_TOKENS   = 1800


 SYSTEM_PROMPT = """You are SafeMedAI, an accurate medicine information assistant.

CRITICAL RULES:
1. NEVER guess or assume a medicine name. If you are not 100% sure about the medicine, say so clearly.
2. NEVER rename or substitute the medicine the user asked about.
3. If the medicine name is unfamiliar or possibly misspelled, still use the EXACT name the user gave.
4. Do not say "this might be referring to..." or suggest alternative medicines.
5. If you have no reliable information about this exact medicine, honestly fill the fields with "This medicine could not be identified. Please verify the name with your doctor or pharmacist."

Return ONLY a valid JSON object:
{
  "medicine_name": "Use the EXACT name the user provided, do not change it",
  "used_for": "Only if you are 100% sure about this medicine, otherwise write: Could not verify this medicine. Please check the name with your pharmacist.",
  "side_effects": "Only if verified, otherwise: Could not verify this medicine.",
  "warnings": "Only if verified, otherwise: Please consult your doctor or pharmacist to verify this medicine name.",
  "food_interactions": "Only if verified, otherwise: Information not available.",
  "storage": "Only if verified, otherwise: Please verify medicine name first.",
  "consult_doctor": "Always consult your doctor or pharmacist to confirm medicine name and usage.",
  "summary": "Only provide a summary if you are completely sure this is a real medicine you recognize."
}

Return ONLY JSON. No extra text. No markdown."""


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
