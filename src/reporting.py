import os
from google import genai
from google.genai import types

def generate_operations_report(csv_data: str) -> str:
    """
    Ingests internal administrative data, runs a specialized analytical engine using
    Gemini-2.5-Flash, and returns structured markdown insights for clinical staff.
    """
    # Initialize the client. It pulls GEMINI_API_KEY directly from environment variables.
    client = genai.Client()

    reporting_instruction = (
        "You are a Senior Clinical Operations & Business Intelligence Analyst for SleepNavigator.\n"
        "Your task is to analyze raw administrative data and generate an executive overview report.\n"
        "Be direct, data-driven, and highlight operational risks to reveal critical performance gaps.\n\n"
        "Format your output clearly with two explicit markdown headings:\n"
        "### 📋 EXECUTIVE NARRATIVE SUMMARY\n"
        "Provide a 2-3 sentence macro overview synthesizing the network's overall efficiency.\n\n"
        "### 🚨 AUTOMATED ANOMALY ALERTS\n"
        "Scan the metrics row-by-row. Isolate any clinics failing our targeted operational benchmarks:\n"
        "- Target Cancellation Rate: < 12%\n"
        "- Target Missing Prior Authorization Rate: < 5%\n\n"
        "For each anomaly, list the Clinic, the metric violation, and the direct impact on revenue or resources."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Analyze this raw dataset:\n\n{csv_data}",
            config=types.GenerateContentConfig(
                temperature=0.1,  # Lower temperature for deterministic analytics mapping
                system_instruction=reporting_instruction,
            ),
        )
        return response.text
    except Exception as e:
        return f"⚠️ **Analytical Engine Error:** Unable to compute data matrices. Details: {str(e)}"