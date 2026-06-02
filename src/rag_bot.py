from pathlib import Path
import re
from src.safety import classify_safety


KNOWLEDGE_BASE_DIR = Path("data/knowledge_base")

STOPWORDS = {
    "the", "is", "a", "an", "to", "of", "and", "or", "in", "on", "for",
    "with", "where", "what", "when", "how", "do", "does", "i", "my",
    "your", "me", "can", "should", "are", "be", "it", "at", "by",
    "from", "this", "that", "there", "about", "please", "patient",
    "patients", "sleep", "study", "appointment", "lab", "labs", "testing", "test", "support", "home"
}


def get_bot_intro() -> str:
    return (
        "Hi, I'm Odette, the SleepNavigator virtual assistant! I'm an AI chatbot "
        "here to help you with clinic locations, sleep study prep, and general FAQs.\n\n"
        "Please note: I cannot provide medical advice, diagnoses, or treatment "
        "recommendations. Always consult with a qualified healthcare provider for "
        "medical concerns.\n\n"
        "If you are experiencing a medical emergency, please call 911 or visit the "
        "nearest emergency room. How can I help you today?"
    )


def clean_words(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()
    return {word for word in words if word not in STOPWORDS and len(word) > 2}


def load_documents() -> list[str]:
    documents = []

    # These files are for safety logic/documentation, not normal RAG answers.
    excluded_files = {
        "safety_guardrails.txt",
        "approved_disclaimer.txt",
    }

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        if file_path.name in excluded_files:
            continue

        text = file_path.read_text(encoding="utf-8")
        documents.append(text)

    return documents


def split_into_chunks(documents: list[str]) -> list[str]:
    chunks = []

    for doc in documents:
        lines = [line.strip() for line in doc.splitlines() if line.strip()]

        current_heading = ""
        current_text = []

        for line in lines:
            # Treat short non-sentence lines as headings.
            # Example: "Food, Eating, and Caffeine Instructions"
            if len(line.split()) <= 10 and not line.endswith("."):
                if current_text:
                    chunks.append(current_heading + "\n" + " ".join(current_text))
                    current_text = []

                current_heading = line
            else:
                current_text.append(line)

        if current_text:
            chunks.append(current_heading + "\n" + " ".join(current_text))

    return chunks


def score_chunk(question: str, chunk: str) -> int:
    question_words = clean_words(question)
    chunk_words = clean_words(chunk)

    score = 0

    # 1. Normal word overlap
    overlap = question_words.intersection(chunk_words)
    score += len(overlap)

    # 2. Strong heading match
    lines = chunk.splitlines()
    if lines:
        heading = lines[0]
        heading_words = clean_words(heading)
        heading_overlap = question_words.intersection(heading_words)
        score += len(heading_overlap) * 12

    # 3. Important question words matter more
    weak_words = {
        "clinic", "help", "information", "instructions", "general",
        "location", "locations", "sleep", "study", "patient", "patients",
        "appointment", "lab", "labs", "testing", "test", "support", "home"
    }

    important_question_words = question_words - weak_words
    important_overlap = important_question_words.intersection(chunk_words)
    score += len(important_overlap) * 6

    # 4. Very strong boost when the main action word appears in the heading
    # This is still general because it works for any heading, not only sleep prep.
    if lines:
        heading_lower = lines[0].lower()
        for word in important_question_words:
            if word in heading_lower:
                score += 15

    return score


def retrieve_best_chunks(question: str, chunks: list[str], top_k: int = 1) -> list[str]:
    scored = []

    for chunk in chunks:
        score = score_chunk(question, chunk)
        scored.append((score, chunk))

    scored.sort(reverse=True, key=lambda x: x[0])

    best_chunks = []

    for score, chunk in scored[:top_k]:
        if score > 0:
            best_chunks.append(chunk)

    return best_chunks


def remove_heading(chunk: str) -> str:
    lines = chunk.splitlines()

    if len(lines) > 1:
        return " ".join(lines[1:]).strip()

    return chunk.strip()


def answer_question(question: str) -> str:
    user_input = question.lower().strip()

    if user_input in ["hi", "hello", "hey", "start"]:
        return get_bot_intro()

    safety = classify_safety(question)

    if not safety["safe"]:
        return safety["message"]

    documents = load_documents()

    if not documents:
        return "No SleepNavigator knowledge base documents are loaded yet."

    chunks = split_into_chunks(documents)
    best_chunks = retrieve_best_chunks(question, chunks, top_k=1)

    if not best_chunks:
        return (
            "I could not find that information in the current SleepNavigator knowledge base. "
            "Please contact SleepNavigator staff for help."
        )

    clean_answers = [remove_heading(chunk) for chunk in best_chunks]
    return "\n\n".join(clean_answers)