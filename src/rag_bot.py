import os
import re 
from google import genai
from google.genai import types
from src.safety import evaluate_intent_and_safety

# Initialize the live Gemini client.
client = genai.Client()


MOCK_PATIENT_DB = {
"corbin ramsey": {
        "dob": "05/07/1994",
        "location": "Heart Hospital of Austin",
        "date": "June 18, 2026",
        "time": "8:30 PM",
        "instructions": "Enter through the Emergency Room entrance and check in at the front desk."
    }
}

def secure_patient_lookup(user_input: str) -> str:
    """
    Simulates a secure database lookup gate. 
    Returns appointment details if Name and DOB match, otherwise handles verification failures.
    """
    cleaned_input = user_input.lower()

    # check if the known patient name is mentioned in the input
    matched_name = None
    for name in MOCK_PATIENT_DB.keys():
        if name in cleaned_input:
            matched_name = name
            break

    # if no matching patient name is found in the text, pass to the standard RAG pipeline
    if not matched_name:
        return ""
    
    # Extract expected DOB for the matched patient
    expected_dob = MOCK_PATIENT_DB[matched_name]["dob"]

    # verify the date of birth  (checks with or without the standard slashes)
    if expected_dob in cleaned_input or expected_dob.replace("/", "") in cleaned_input:
        patient_data = MOCK_PATIENT_DB[matched_name]
        return (
            f"\n\n--- Source: Secure SleepNav Database (Patient Profile: {matched_name.title()}) ---\n"
            f"The patient's name is confirmed as {matched_name.title()}.\n"
            f"Their appointment location is the {patient_data['location']}.\n"
            f"The test date is explicitly scheduled for {patient_data['date']} at {patient_data['time']}.\n"
            f"Special directions for arrival: {patient_data['instructions']}\n"
        )
    
    #name matched but DOB was missing or incorrect
    return "REFUSE_VERIFICATION"

# ============== Rag Retrieval Functions ==============

def load_all_knowledge_base_files() -> str:
    """
    Scans the knowledge_base directory and combine all text files into a single context string for RAG retrieval.
    Injects source tags so the model knows where boundaries exist between clinical rules.
    """
    kb_dir = os.path.join("data", "knowledge_base")
    combined_context = ""

    #catch missing directories cleanly before we try to read files
    if not os.path.exists(kb_dir):
        return "Knowledge base directory missing."
    
    for file_name in os.listdir(kb_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(kb_dir, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_context += f"\n--- Source: {file_name} ---\n"
                    combined_context += f.read() + "\n"
            except Exception as e:
                print(f"Warning: Could not read file {file_name}: {e}")

    return combined_context

def answer_question(question: str) -> str:
    """
    Evaluates safety filters first, then synthesizes a grounded answer from local files.
    """
    triage = evaluate_intent_and_safety(question)
    category = triage.get("category")
    
    # 1. EXPLICIT DANGER REFUSALS
    if triage.get("requires_refusal") or category in ["medical_advice", "crisis_emergency"]:
        return (
            " **Safety Notice:** I am a virtual administrative assistant and cannot provide medical advice, "
            "interpret test results, or recommend treatments.\n\n"
            "If you are experiencing a medical emergency (such as severe chest pain or respiratory distress), "
            "or a health crisis, please immediately call 911 or visit the nearest emergency room. You can "
            "also text or call 988 for the Suicide & Crisis Lifeline.\n\n"
            "For non-emergency clinical or administrative inquiries, please contact your sleep specialist "
            "directly at 800-892-9994 or send a secure message through your patient portal."
        )
    
    # run the secure verification CHECK fro Personal Schedules
    patient_context = secure_patient_lookup(question)

    if patient_context == "REFUSE_VERIFICATION":
        return(
            "**Identity Verification Required:** I see you are asking about specific appointment details. "
            "To comply with HIPAA security requirements, please provide your full name and Date of Birth "
            "formatted as (MM/DD/YYYY) so I can securely verify your patient file."
        )

    # 2. LOAD REAL KNOWLEDGE CONTEXT FOR ALL SAFE QUESTIONS
    context = load_all_knowledge_base_files()

    # if identity was verified, append the private database snippet right into the model's context window
    if patient_context:
        context += patient_context

    # 3. PROMPT GEMINI WITH STRICT GROUNDING INSTRUCTIONS
    rag_instruction = (
        "You are Odette, the virtual administrative assistant for SleepNavigator. "
        "Your task is to answer patient logistical and prep questions using ONLY the provided context text.\n\n"
        "Strict Grounding Rules:\n"
        "1. Base your response strictly on facts explicitly written inside the context source text.\n"
        "2. CHITCHAT EXCEPTION: If the user is just engaging in casual conversation or small talk "
        "(e.g., 'Hey', 'Hello', 'How are you?'), respond politely as Odette without repeating your entire "
        "legal introduction disclaimer, and ask how you can help them with their sleep study logistics today.\n"
        "3. If the context does not explicitly contain the answer to a logistical question, and it is not basic chitchat, "
        "reply exactly with: 'I could not find that specific information in the current SleepNavigator "
        "knowledge base. Please contact SleepNavigator staff for help.'\n"
        "4. Never guess, assume, or hallucinate schedules, directions, phone numbers, or doors."
    )

    prompt = f"Retrieved Context:\n{context}\n\nPatient Question: {question}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=rag_instruction,
                temperature=0.1   # Low temperature ensures it sticks strictly to context details
            )
        )
        return response.text
    except Exception as e:
        return f"Error communicating with assistant backend: {str(e)}"

def get_bot_intro() -> str:
    """
    Returns company-approved legal disclaimer to inject directly to inject directly into frintend loaders
    """
    return (
        "Hi, I'm Odette, the SleepNavigator virtual assistant! I'm an AI chatbot here to help you "
        "with clinic locations, sleep study prep, and general FAQs.\n\n"
        "Please note: I cannot provide medical advice, diagnoses, or treatment recommendations. "
        "Always consult with a qualified healthcare provider for medical concerns.\n\n"
        "If you are experiencing a medical emergency, please call 911 or visit the nearest emergency room.\n\n"
        "How can I help you today?"
    )