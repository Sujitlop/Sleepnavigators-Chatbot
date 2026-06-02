import os
from dotenv import load_dotenv

# 1. CRITICAL: Load environment variables BEFORE importing our src modules
load_dotenv()

# 2. Now import Streamlit and your backend code safely
import streamlit as st
from src.rag_bot import answer_question, get_bot_intro

# 3. Configure the browser tab title and alignment
st.set_page_config(page_title="SleepNavigator Chatbot", page_icon="🌙", layout="centered")

# 4. Render user-facing headers
st.title("SleepNavigator Assistant")
st.caption("Proof of Concept Prototype — Odette Virtual Assistant")

# 5. Initialize chat history in Streamlit's browser session memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": get_bot_intro()}
    ]

# 6. Keep historical chat logs visible on the screen during page refreshes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. Capture user typing from the interactive chat input bar
if user_input := st.chat_input("Ask me about clinic locations, parking, or sleep study prep..."):
    
    # Render the user's message to the UI screen and save to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # Send the input straight into your verified backend pipeline
    with st.chat_message("assistant"):
        with st.spinner("Odette is checking project materials..."):
            bot_response = answer_question(user_input)
            st.write(bot_response)
            
    # Save the assistant's response to history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})