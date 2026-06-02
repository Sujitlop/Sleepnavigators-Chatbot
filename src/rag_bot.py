import os
from google import genai
from google.genai import types
from src.safety import evaluate_intent_and_safety

client = genai.Client()

def load_all_knowledge_base_files() -> str:
    kb_dir = os.path.join("data", "knowledge_base")
    combined_context = ""
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
        if category == "medical_advice":
            return (
                "I am a virtual administrative assistant and cannot provide medical advice, "
                "interpret test results, or recommend treatments. For your safety, please contact your "
                "sleep specialist directly at 800-892-9994 or send a message through your secure "
                "patient portal. If you are experiencing a medical emergency, please call 911."
            )
        elif category == "crisis_emergency":
            return (
                "This situation may be urgent. If you are experiencing a medical emergency (such as chest pain) "
                "or a mental health crisis, please immediately call 911 or visit the nearest "
                "emergency room. You can also text or call 988 for the Suicide & Crisis Lifeline."
            )

    # 2. LOAD REAL KNOWLEDGE CONTEXT FOR ALL SAFE QUESTIONS
    context = load_all_knowledge_base_files()

    # 3. PROMPT GEMINI WITH STRICT GROUNDING INSTRUCTIONS
    rag_instruction = (
        "You are Odette, the virtual administrative assistant for SleepNavigator. "
        "Your task is to answer patient logistical and prep questions using ONLY the provided context text.\n\n"
        "Strict Grounding Rules:\n"
        "1. Base your response strictly on facts explicitly written inside the context source text.\n"
        "2. If the context does not explicitly contain the answer to the user's specific question "
        "(or if they are asking completely random trivia like sports or programming), do not invent details. "
        "Instead, reply exactly with: 'I could not find that specific information in the current SleepNavigator "
        "knowledge base. Please contact SleepNavigator staff for help.'\n"
        "3. Never guess, assume, or hallucinate schedules, directions, phone numbers, or doors."
    )

    prompt = f"Retrieved Context:\n{context}\n\nPatient Question: {question}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=rag_instruction,
                temperature=0.1
            )
        )
        return response.text
    except Exception as e:
        return f"Error communicating with assistant backend: {str(e)}"

def get_bot_intro() -> str:
    return (
        "Hi, I'm Odette, the SleepNavigator virtual assistant! I'm an AI chatbot here to "
        "help you with clinic locations, sleep study prep, and general FAQs.\n\n"
        "Please note: I cannot provide medical advice, diagnoses, or treatment recommendations."
    )