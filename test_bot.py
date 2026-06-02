from src.rag_bot import answer_question, get_bot_intro

def main():
    print("SleepNavigator Text-Based RAG Bot Prototype")
    print("-" * 60)
    print(get_bot_intro())
    print("-" * 60)
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        question = input("Patient question: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        answer = answer_question(question)

        print()
        print("Odette: ")
        print(answer)
        print("-"*60)

if __name__ == "__main__":
    main()