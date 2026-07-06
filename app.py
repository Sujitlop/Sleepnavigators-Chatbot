import os
from collections import Counter
from dotenv import load_dotenv

# 1. CRITICAL: Load environment variables BEFORE importing our src modules
load_dotenv()

# 2. Now import Streamlit and your backend code safely
import streamlit as st
from src.rag_bot import answer_question, get_bot_intro

# 3. Configure the browser tab title and alignment
st.set_page_config(page_title="SleepNavigator Chatbot", page_icon="🌙", layout="wide")

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


def render_patient_chat() -> None:
    st.title("SleepNavigator Assistant")
    st.caption("Proof of Concept Prototype — Odette Virtual Assistant")

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


def render_staff_analytics() -> None:
    st.title("Internal Staff Analytics View")
    st.caption("Operational summary for the SleepNavigator assistant")

    analytics = st.session_state.analytics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions handled", analytics["questions"])
    with col2:
        st.metric("Resolved", analytics["resolved"])
    with col3:
        st.metric("Refused", analytics["refused"])
    with col4:
        st.metric("Emergency escalations", analytics["emergency"])

    st.subheader("Topic breakdown")
    if analytics["topics"]:
        topic_data = dict(analytics["topics"].most_common())
        st.bar_chart(topic_data)
    else:
        st.info("No interaction data yet.")

    st.subheader("Recent interactions")
    if analytics["recent"]:
        for item in analytics["recent"]:
            st.write(f"- {item['question']} — {item['topic']} ({item['outcome']})")
    else:
        st.info("No recent interactions recorded.")


view_mode = st.sidebar.radio(
    "View",
    ["Patient Chat", "Internal Staff Analytics"],
    index=0,
    help="Switch between the patient-facing chatbot and the internal staff dashboard.",
)

if view_mode == "Internal Staff Analytics":
    render_staff_analytics()
else:
    render_patient_chat()