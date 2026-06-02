import os
from dotenv import load_dotenv
# Load environment variables from the .env file at startup
load_dotenv()
# Now import your backend code safely
from src.rag_bot import answer_question, get_bot_intro



def main():
    # Sanity check to ensure the API key is accessible
    if not os.getenv("GEMINI_API_KEY"):
        print("CRITICAL ERROR: GEMINI_API_KEY is missing from your .env file.")
        return

    print("SleepNavigator Text-Based RAG Bot Prototype (Live Gemini API)")
    print("-" * 60)
    print(get_bot_intro())
    print("-" * 60)
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        # Capture patient input from the console
        question = input("Patient question: ").strip()

        # Handle blank submissions safely
        if not question:
            continue

        # Exit conditions to break out of the script loop
        if question.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        # Process the question through your dynamic guardrails and file-reader pipeline
        answer = answer_question(question)

        print()
        print("Odette:")
        print(answer)
        print("-" * 60)

if __name__ == "__main__":
    main()