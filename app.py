import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import openai
from dotenv import load_dotenv
import os
import datetime
import ctypes.wintypes

# return desktop path
def get_windows_desktop_path():
    CSIDL_DESKTOP = 0x0000
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value


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

# Storing conversation history
chat_log = []

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
        if not user_input:
            print("⚠️ Input cannot be empty. ⚠️")
        messages.append({"role": "user", "content": user_input})
        chat_log.append(f"You: {user_input}")

        try:
            response = openai.ChatCompletion.create(model=OPENAI_MODEL,messages=messages)
            reply = response.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": reply})
            chat_log.append(f"GPT-4o: {reply}")
            print("GPT-4o:", reply)
        # If user hit rate limit display error message
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
            print("⚠️ Input cannot be empty. Try again. ⚠️")
            continue

        chat_log.append(f"You: {user_input}")

        try:
            response = chat_session.send_message(user_input)
            reply = response.text
            chat_log.append(f"Gemini: {reply}")
            print("Gemini:", reply)
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

# Saving chatlog as .txt file
if chat_log:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # filename depends on which model is used
    filename = f"chat_log_{'openai' if choice == '1' else 'gemini'}_{timestamp}.txt"

    # mapping desktop path to desktop_path variable
    desktop_path = get_windows_desktop_path()
    if not os.path.exists(desktop_path):
        desktop_path = "."  # fallback if desktop doesn't exist
    # getting full path to desktop
    full_path = os.path.join(desktop_path, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chat_log))

    print("Saving to:", desktop_path)
    print(f"\n📝 Chat log saved to '{filename}' 📝")

