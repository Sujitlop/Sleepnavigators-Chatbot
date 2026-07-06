# SleepNavigator AI Chatbot

A proof-of-concept conversational assistant for SleepNavigator that helps patients with clinic logistics, sleep-study preparation, and general FAQs using a retrieval-augmented generation (RAG) workflow.

The chatbot is designed to be helpful while staying within a strict safety boundary. It can answer administrative questions grounded in local source documents, but it refuses medical advice or emergency-related requests and routes urgent concerns to appropriate escalation guidance.

## Overview

This project combines:

- A Streamlit web chat interface for interactive use
- A Python backend that grounds responses in local knowledge-base files
- A lightweight safety classifier for medical and crisis-related requests
- A mock secure patient lookup pathway for appointment-specific information
- A console-based demo mode for quick testing

The assistant is intended to support questions such as:

- clinic locations and parking instructions
- sleep-study preparation rules
- after-hours support workflows
- general FAQ-style administrative information

## Project Structure

```text
.
├── app.py                  # Streamlit web app entry point
├── test_bot.py             # Console-based demo runner
├── requirements.txt        # Python dependencies
├── test_questions.md       # Example test prompts and scenarios
├── data/
│   └── knowledge_base/     # Local source documents used for RAG grounding
│       ├── after_hours_support.txt
│       ├── approved_disclaimer.txt
│       ├── lab_locations.txt
│       ├── safety_guardrails.txt
│       ├── sleep_study_prep.txt
│       └── sleepnavigator_faq.txt
└── src/
    ├── rag_bot.py          # Core answer-generation pipeline
    ├── safety.py           # Safety triage classification
    └── __init__.py
```

## How It Works

### 1. Safety triage

The app first sends the user's message to a safety classifier in [src/safety.py](src/safety.py). This layer identifies whether the request is:

- safe to proceed for administrative support
- a medical-advice request that should be refused
- an emergency or crisis situation that requires escalation

### 2. Knowledge-grounded answering

For safe requests, [src/rag_bot.py](src/rag_bot.py) loads the text files in the knowledge base and builds a context window from them. The model is instructed to answer only from that context and to avoid hallucinating facts.

### 3. Secure patient lookup

The bot also includes a mock secure lookup flow for appointment-specific information. If a user mentions a known patient name and provides a matching DOB, the system can surface appointment details; otherwise, it prompts for verification rather than exposing protected information.

## Features

- Grounded responses from local documents instead of relying only on general model knowledge
- Strong refusal behavior for medical advice, diagnosis, and treatment requests
- Emergency escalation guidance for urgent situations
- Streamlit chat interface for a polished user experience
- Terminal-based testing mode for rapid validation

## Requirements

- Python 3.9+
- A Google Gemini API key

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project root with your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

## Running the App

### Web app with Streamlit

```bash
streamlit run app.py
```

This opens the SleepNavigator assistant in your browser.

### Console demo

```bash
python test_bot.py
```

This runs a text-based version of the bot in the terminal.

## Example Questions

You can try prompts such as:

- Where do I park for the Methodist Main lab?
- What should I bring to my sleep study?
- What happens if I call after hours and no one answers?
- Can I change my CPAP settings?
- I am having severe chest pain right now.

## Safety and Compliance Notes

This prototype is intentionally conservative. It is not a substitute for medical care and is limited to administrative and logistical support. The bot will refuse requests that involve:

- treatment changes
- interpretation of sleep study results
- medication dosing advice
- mental-health counseling
- urgent medical emergencies

For genuine medical concerns, the bot directs users to emergency services or their care team.

## Testing

The repository includes sample test prompts in [test_questions.md](test_questions.md) covering:

- clinic locations and logistics
- sleep-study preparation
- after-hours support
- medical-advice refusal cases
- emergency escalation cases
- out-of-scope fallback responses

## Notes

This project is a prototype and should be treated as a demonstration of safe, grounded conversational AI for a healthcare-adjacent workflow. It uses local source documents and a lightweight safety layer to reduce hallucinations and inappropriate medical guidance.
