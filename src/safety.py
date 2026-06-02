URGENT_RESPONSE = (
    "I’m sorry you’re experiencing that. This may be urgent. "
    "Please call 911 or go to the nearest emergency room immediately. "
    "Do not wait for a chatbot response if you may be having a medical emergency."
)

MEDICAL_ADVICE_RESPONSE = (
    "I am a virtual administrative assistant and cannot provide medical advice, "
    "interpret test results, or recommend treatments. For your safety, please "
    "contact your sleep specialist directly at 800-892-9994 or send a "
    "message through your secure patient portal. If you are experiencing a medical "
    "emergency, please call 911 or go to the nearest emergency room immediately."
)

URGENT_KEYWORDS = [
    "severe shortness of breath",
    "shortness of breath",
    "can't breathe",
    "cannot breathe",
    "chest pain",
    "racing heart",
    "choking",
    "gasping",
    "unable to catch my breath",
    "can't catch my breath",
    "falling asleep while driving",
    "fell asleep while driving",
    "operating machinery",
    "severe morning headache",
    "confusion",
    "dizziness",
    "weakness",
    "self-harm",
    "self harm",
    "suicidal",
    "suicide",
    "kill myself",
    "severe mental distress",
]

REFUSED_MEDICAL_KEYWORDS = [
    # Diagnosis
    "diagnose",
    "diagnosis",
    "do i have sleep apnea",
    "do i have narcolepsy",
    "do i have insomnia",
    "what condition do i have",

    # Result interpretation
    "interpret my sleep study",
    "explain my sleep study",
    "sleep study results",
    "polysomnography report",
    "ahi score",
    "cpap adherence data",
    "blood work",

    # Medication advice
    "medication",
    "medicine",
    "prescription",
    "sleep aid",
    "melatonin",
    "dosage",
    "dose",
    "start taking",
    "stop taking",
    "adjust my medication",

    # Mental health counseling
    "anxiety",
    "depression",
    "counseling",
    "psychiatric",
    "mental health",
]

TREATMENT_DEVICES = [
    "cpap",
    "bipap",
    "pap",
    "mask",
    "oxygen",
    "oxygen flow",
    "pressure",
    "preassure",  # common typo
    "setting",
    "settings",
]

ADJUSTMENT_WORDS = [
    "change",
    "adjust",
    "increase",
    "decrease",
    "raise",
    "lower",
    "modify",
    "switch",
    "stop",
    "start",
]


def classify_safety(user_question: str) -> dict:
    question = user_question.lower().strip()

    # 1. Urgent / emergency symptoms
    for keyword in URGENT_KEYWORDS:
        if keyword in question:
            return {
                "safe": False,
                "type": "urgent",
                "message": URGENT_RESPONSE,
            }

    # 2. Refused medical-advice questions
    for keyword in REFUSED_MEDICAL_KEYWORDS:
        if keyword in question:
            return {
                "safe": False,
                "type": "medical_advice",
                "message": MEDICAL_ADVICE_RESPONSE,
            }

    # 3. General treatment-adjustment protection
    # This catches questions like:
    # "Can I change my CPAP pressure?"
    # "Can I adjust my BiPAP settings?"
    # "Can I increase my oxygen flow?"
    # "Can I switch my mask type?"
    # "Can I stop using CPAP?"
    has_treatment_device = any(device in question for device in TREATMENT_DEVICES)
    has_adjustment_action = any(action in question for action in ADJUSTMENT_WORDS)

    if has_treatment_device and has_adjustment_action:
        return {
            "safe": False,
            "type": "medical_advice",
            "message": MEDICAL_ADVICE_RESPONSE,
        }

    # 4. If safe, allow RAG search
    return {
        "safe": True,
        "type": "safe",
        "message": "",
    }