import os
from dotenv import load_dotenv
from google import genai

print("Starting Gemini API test...")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "paste_key_here_later":
    print("ERROR: GEMINI_API_KEY is missing.")
    exit()

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say: Gemini API is working."
)

print("Response received:")
print(response.text)