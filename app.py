import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import openai
from dotenv import load_dotenv
import os

# Used for loading environment variables
load_dotenv()

# API KEYS
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Defining which model to use
GOOGLE_MODEL = "gemini-2.5-flash"
OPENAI_MODEL = "gpt-4o"

# Linking model with API
genai.configure(api_key=GOOGLE_API_KEY)
openai.api_key = OPENAI_API_KEY

# User chooses which model to use
print("Choose your AI model:")
print("1. OpenAI ChatGPT")
print("2. Google Gemini")
choice = input("Enter 1 or 2: ").strip()

if choice == '1':
    print(f"\nChat with OpenAI GPT-4o - type 'stop' to exit.")
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'stop':
            break
        messages.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(model=OPENAI_MODEL,messages=messages)
            reply = response.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": reply})
            print("GPT-4o:", reply)
        except openai.error.RateLimitError:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌")
            print("❌ You’ve run out of OpenAI usage today or exceeded your quota.❌")
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌")
            print("Visit https://platform.openai.com/account/usage to check your usage.\n")
            break
elif choice == '2':
    model = genai.GenerativeModel(GOOGLE_MODEL)
    chat_session = model.start_chat()

    print(f"\nChat with Google Gemini ({GOOGLE_MODEL}) — type 'stop' to exit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "stop":
            break
        if not user_input:
            print("⚠️ Input cannot be empty. Try again.")
            continue

        try:
            response = chat_session.send_message(user_input)
            print("Gemini:", response.text)
        except ResourceExhausted:
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌")
            print("❌         You’ve hit your Gemini rate limit or quota.            ❌")
            print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌")
            print("Visit https://makersuite.google.com/app/apikey to check usage.\n")
            break
        except Exception as e:
            print("❌ Error:", str(e))
            break
else:
    print("Invalid choice. Exiting...")

