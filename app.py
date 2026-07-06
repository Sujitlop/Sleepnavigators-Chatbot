import os
from dotenv import load_dotenv

# 1. CRITICAL: Load environment variables BEFORE importing our src modules
load_dotenv()

# 2. Now import Streamlit and your backend code safely
import streamlit as st
from src.rag_bot import answer_question, get_bot_intro

# 3. Configure the browser tab title and alignment
st.set_page_config(page_title="SleepNavigator Chatbot", page_icon="🌙", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .chat-shell {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }
    .composer {
        margin-top: 0.75rem;
        padding: 0.75rem;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        background: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. Render user-facing headers
st.title("SleepNavigator Assistant")
st.caption("Proof of Concept Prototype — Odette Virtual Assistant")

# 5. Initialize chat history in Streamlit's browser session memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": get_bot_intro()}
    ]

# 6. Keep historical chat logs visible in a dedicated conversation area
st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="composer">', unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Type your message",
        placeholder="Ask me about clinic locations, parking, or sleep study prep...",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 7. Handle the submitted message and refresh the UI
if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.chat_message("user"):
        st.write(user_input.strip())

    with st.chat_message("assistant"):
        with st.spinner("Odette is checking project materials..."):
            bot_response = answer_question(user_input.strip())
            st.write(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()