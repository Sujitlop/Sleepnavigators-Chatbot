import os
import json
from google import genai
from google.genai import types

#initialize the Gemini client. It pulls the GEMINI_API_key directly from environment variables. 
def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(
        api_key=api_key,
        http_options={"max_retries": 3}
        )

def evaluate_intent_and_safety(user_question: str) -> dict:
    client = get_client()

    """
    Triage classifier focused strictly on filtering out medical advice and crises.
    Passes all other queries (logistics, small talk, trivia) to the grounding layer.
    """
    # Simple instructions for themodel to behave like a strict administrative router.
    triage_instruction = (
            "You are an automated triage classifier for a sleep medical center chatbot.\n"
            "Analyze the user query and determine if it requires an immediate medical/crisis refusal. "
            "Respond STRICTLY in JSON format with exactly two keys:\n"
            "1. 'category': Must be exactly one of these strings:\n"
            "   - 'medical_advice' (e.g., requests to alter CPAP/BiPAP settings, mask fitment adjustments, sleep posture inquiries, interpreting AHI/medical test scores, medication/melatonin dosing changes)\n"
            "   - 'crisis_emergency' (e.g., chest pain, racing heart, respiratory distress, choking/gasping for air, falling asleep while driving, extreme sudden daytime sleepiness, severe morning headaches with confusion/dizziness, thoughts of self-harm/suicidal ideation)\n"
            "   - 'safe_to_proceed' (Any location questions, directions, parking, door descriptions, pack lists, small talk, or off-topic questions)\n"
            "2. 'requires_refusal': boolean (true if category is medical_advice or crisis_emergency, false if safe_to_proceed)"
        )

    try:
        #Use gemini-2.5-flash for rapid classification to keep the bot feeling responsive. 
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_question,
            config=types.GenerateContentConfig(
                system_instruction=triage_instruction,
                response_mime_type="application/json",
                temperature=0.0 # force deterministic output so classification stay consistant
            )
        )
        # Parse the JSON response safely. If the model output is not valid JSON, this will raise an exception and we can default to safe behaviour.
        return json.loads(response.text)
    except Exception:
        # Secure fallback: if the API behaves weirdly, let it drop through to the text documents safely
        return {"category": "safe_to_proceed", "requires_refusal": False}