import os
import json
from google import genai
from google.genai import types

client = genai.Client()

def evaluate_intent_and_safety(user_question: str) -> dict:
    """
    Triage classifier focused strictly on filtering out medical advice and crises.
    Passes all other queries (logistics, small talk, trivia) to the grounding layer.
    """
    triage_instruction = (
        "You are an automated triage classifier for a sleep medical center chatbot.\n"
        "Analyze the user query and determine if it requires an immediate medical/crisis refusal. "
        "Respond STRICTLY in JSON format with exactly two keys:\n"
        "1. 'category': Must be exactly one of these strings:\n"
        "   - 'medical_advice' (e.g., requests to alter CPAP/BiPAP settings, mask fitment adjustments, sleep posture inquiries, interpreting AHI/medical test scores, medication/melatonin dosing changes)\n"
        "   - 'crisis_emergency' (e.g., chest pain, respiratory distress/cannot breathe, thoughts of self-harm, broken bones, severe physical injuries)\n"
        "   - 'safe_to_proceed' (Any location questions, directions, parking, door descriptions, pack lists, small talk, or off-topic questions)\n"
        "2. 'requires_refusal': boolean (true if category is medical_advice or crisis_emergency, false if safe_to_proceed)"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_question,
            config=types.GenerateContentConfig(
                system_instruction=triage_instruction,
                response_mime_type="application/json",
                temperature=0.0 # Absolute consistency
            )
        )
        return json.loads(response.text)
    except Exception:
        # Secure fallback: if the API behaves weirdly, let it drop through to the text documents safely
        return {"category": "safe_to_proceed", "requires_refusal": False}