import os
from collections import Counter
from dotenv import load_dotenv

# 1. CRITICAL: Load environment variables BEFORE importing our src modules
load_dotenv()

# 2. Now import Streamlit and your backend code safely
import streamlit as st
from src.rag_bot import answer_question, get_bot_intro

# 3. Configure the browser tab title and alignment
st.set_page_config(page_title="SleepNavigator AI Suite", page_icon="🌙", layout="wide")

# 4. Initialize chat history in Streamlit's browser session memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": get_bot_intro()}
    ]

if "analytics" not in st.session_state:
    st.session_state.analytics = {
        "questions": 0,
        "resolved": 0,
        "refused": 0,
        "emergency": 0,
        "topics": Counter(),
        "recent": [],
    }


def get_topic_label(question: str) -> str:
    q = question.lower()

    if any(term in q for term in ["chest pain", "shortness of breath", "choking", "driving", "911", "988", "suicidal", "self-harm"]):
        return "urgent escalation"
    if any(term in q for term in ["cpap", "bipap", "pressure", "mask", "ahi", "score", "melatonin", "medication", "treatment", "diagnosis", "results"]):
        return "medical advice"
    if any(term in q for term in ["parking", "location", "address", "door", "clinic", "lab", "where", "entrance"]):
        return "clinic logistics"
    if any(term in q for term in ["bring", "pajamas", "pillow", "hair", "shower", "nails", "snacks", "coffee", "caffeine", "dinner", "water"]):
        return "prep guidance"
    if any(term in q for term in ["after hours", "answering", "phone", "call"]):
        return "after-hours support"
    return "general faq"


def update_analytics(question: str, response: str) -> None:
    analytics = st.session_state.analytics
    analytics["questions"] += 1

    response_text = response.lower()
    if "safety notice" in response_text or "identity verification required" in response_text:
        analytics["refused"] += 1
        outcome = "refused"
    elif any(term in response_text for term in ["911", "988", "medical emergency", "urgent"]):
        analytics["emergency"] += 1
        outcome = "emergency"
    else:
        analytics["resolved"] += 1
        outcome = "resolved"

    topic = get_topic_label(question)
    analytics["topics"][topic] += 1
    analytics["recent"].append({
        "question": question.strip(),
        "topic": topic,
        "outcome": outcome,
    })
    if len(analytics["recent"]) > 8:
        analytics["recent"] = analytics["recent"][-8:]


def render_part_a() -> None:
    st.title("Part A: After-Hours Concierge Bot")
    st.caption("A RAG-powered assistant for sleep-study logistics, clinic information, and prep guidance.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Ask me about clinic locations, parking, or sleep study prep..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Odette is checking project materials..."):
                bot_response = answer_question(user_input)
                st.write(bot_response)

        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        update_analytics(user_input, bot_response)
        st.rerun()


def render_part_b() -> None:
    st.title("Part B: Next-Gen AI Reporting Concepts")
    st.caption("A proof of concept for conversational BI, narrative summaries, and anomaly detection.")

    st.markdown(
        "This internal reporting view is designed to move beyond static data grids by combining natural-language requests, generated insight summaries, and proactive anomaly alerts."
    )

    st.subheader("Core concepts")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Conversational BI")
        st.write("Staff can ask questions like: 'Show me the top 3 clinics by patient volume this month.'")
    with col2:
        st.markdown("### Narrative Summaries")
        st.write("The system can turn report data into a short executive summary that explains what changed and why it matters.")
    with col3:
        st.markdown("### Anomaly Detection")
        st.write("Historical patterns can be scanned to flag unusual patient volume, missing authorizations, or clinic-level outliers.")

    st.subheader("Example staff prompt")
    prompt = st.text_area(
        "Try a sample request",
        value="Show me the top 3 clinics by patient volume this month.",
        height=90,
    )

    if st.button("Generate concept preview"):
        st.success("Concept preview generated")
        st.write(f"Detected intent: {prompt}")
        st.bar_chart({"Heart Hospital of Austin": 42, "WellNecessities": 31, "Methodist Main": 27})
        st.write("Narrative summary: Patient volume is strongest at Heart Hospital of Austin, while WellNecessities shows a moderate decline in this period.")
        st.write("Anomaly alert: One clinic shows a sudden drop in completed authorizations and should be reviewed.")

    st.subheader("Execution plan")
    st.write("- Week 1: Build the knowledge base and RAG bot foundation")
    st.write("- Week 2: Connect the bot to a simple chat or SMS front end")
    st.write("- Weeks 3-5: Generate a reporting PoC using sanitized sample data")
    st.write("- Week 6: Finalize documentation and handoff materials")


view_mode = st.sidebar.radio(
    "Project view",
    ["Part A: After-Hours Concierge Bot", "Part B: Next-Gen AI Reporting Concepts"],
    index=0,
    help="Switch between the patient-facing concierge bot and the internal reporting concepts demo.",
)

if view_mode == "Part B: Next-Gen AI Reporting Concepts":
    render_part_b()
else:
    render_part_a()