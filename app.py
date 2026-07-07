import os
import sys

# 1. CRITICAL CLOUD FIX: Force the root directory into the Python path before local imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from dotenv import load_dotenv

# 2. Load environment variables safely
load_dotenv()

# 3. Import Streamlit and your backend modules safely
import streamlit as st
from src.rag_bot import answer_question, get_bot_intro
from src.reporting import generate_operations_report
from src.database_pipeline import pipeline_verify_and_fetch_appointment, pipeline_fetch_weekly_metrics

# 4. Configure the browser tab title and layout (Wide format for clear analytics grids)
st.set_page_config(page_title="SleepNavigator Portal", page_icon="🌙", layout="wide")


# =========================================================
# --- SIDEBAR: SECURE APPORTIONING FOR INTERNAL STAFF ---
# =========================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=60)
    st.title("Navigation Center")
    st.markdown("---")
    
    # Simple role switcher to model administrative access control
    app_mode = st.radio(
        "Select Portal View:",
        ["💬 Patient Concierge", "📊 Internal Staff Analytics"],
        help="Switch between public patient support and internal clinic reporting."
    )
    
    st.markdown("---")
    st.caption("🔒 Secured Microservice Interface\nIndigo Arc / Summer Session 2026")


# =========================================================
# VIEW 1: USER-FACING CHATBOT CONCIERGE (PART A)
# =========================================================
if app_mode == "💬 Patient Concierge":
    # Everything goes inside our constrained width columns
    left_spacer, chat_col, right_spacer = st.columns([1, 3, 1])
    
    with chat_col:
        st.title("SleepNavigator Assistant")
        st.caption("Proof of Concept Prototype — Odette Virtual Assistant")
        st.markdown("---")
        
        # Initialize chat history in Streamlit's session memory
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": get_bot_intro()}
            ]
        
        # 1. ALWAYS RENDER THE COMPLETE HISTORY FIRST
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # 2. RENDER THE INPUT CONTAINER AT THE ABSOLUTE BOTTOM OF THE COLUMN
        # 2. RENDER THE INPUT CONTAINER AT THE ABSOLUTE BOTTOM OF THE COLUMN
        if user_input := st.chat_input("Ask me about clinic locations, parking, or sleep study prep...", key="patient_chat_input"):
            
            # Step A: Append user query to history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Step B: Run pipeline immediately to prevent the input bar from jumping up
            bot_response = answer_question(user_input)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Step C: Reload the interface so everything renders in perfect chronological order
            st.rerun()


# =========================================================
# VIEW 2: NEXT-GEN AI REPORTING CONCEPTS (PART B — STAFF ONLY)
# =========================================================
else:
    st.title("📊 Next-Gen Clinical Analytics Dashboard")
    st.caption("Internal Operational Intelligence & Automated Anomaly Systems (Staff Access Only)")
    st.markdown("---")
    
    st.markdown("""
    This utility demonstrates **Part B: Next-Gen AI Reporting Concepts**. 
    Clinical staff can upload a sanitized weekly metrics spreadsheet to generate an immediate, 
    human-readable Executive Narrative Summary paired with automated benchmark anomaly tracking.
    """)
    
    # Expandable Sample Template to simplify testing/presentation demo
    with st.expander("📋 View Sample Metrics Template (CSV)"):
        sample_csv = (
            "Clinic_Name,Weekly_Patient_Volume,Cancellation_Rate,Missing_Auth_Rate\n"
            "Austin North Clinic,42,8%,2%\n"
            "Heart Hospital Campus,58,24%,15%\n"
            "Round Rock Center,31,10%,4%\n"
            "Southwest Sleep Hub,19,5%,18%"
        )
        st.code(sample_csv, language="csv")
        st.caption("Copy the block above into a local text file and save as '.csv' to test the engine.")

    # Layout: Split screen to see raw grid on the left, AI generated summaries on the right
    grid_col, insight_col = st.columns([1, 1], gap="large")
    
    with grid_col:
        st.subheader("📁 Data Ingestion Gate")
        uploaded_file = st.file_uploader("Upload Sanitized Weekly Clinic Export", type=["csv"])
        
        if uploaded_file is not None:
            # Parse metrics via pandas to simulate standard BI grid render
            df = pd.read_csv(uploaded_file)
            st.markdown("**Uploaded Data Grid Preview:**")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Convert frame straight back into a standard CSV string block for our LLM function
            csv_payload = df.to_csv(index=False)
            
            st.markdown("---")
            trigger_analysis = st.button("🚀 Compile AI Reporting Summary", type="primary")
    
    with insight_col:
        st.subheader("💡 Business Intelligence Outputs")
        
        if uploaded_file is not None and trigger_analysis:
            with st.spinner("Gemini is processing network data matrices against benchmark criteria..."):
                # Query your newly created src/reporting.py module
                ai_insights = generate_operations_report(csv_payload)
                
                # Render the clean markdown report back to the staff panel
                st.markdown(ai_insights)
        elif uploaded_file is not None:
            st.info("Data uploaded successfully. Click 'Compile AI Reporting Summary' to fire the pipeline.")
        else:
            st.info("Please upload a clinical metrics file in the ingestion panel to initialize the analytics matrix.")