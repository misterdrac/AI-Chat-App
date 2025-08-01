# LIBRARIES
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import os
import datetime
import platform
from pathlib import Path

# PROGRAM LOGIC

# loading environment variables
load_dotenv()
# getting and setting API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
openai.api_key = OPENAI_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

# variables defining models
OPENAI_MODEL = "gpt-4o"
GOOGLE_MODEL = "gemini-2.5-flash"

# variables used by app
chat_log = []
chat_session = None
messages = [{"role": "system", "content": "You are a helpful assistant."}]
current_model = "OpenAI"

# setting the UI
root = tk.Tk()
root.title("Mister Drac's AI Chatbot")
root.geometry("1080x1080")
root.minsize(700, 500)

# Modern style tweaks
style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 10))
style.configure("TCombobox", font=("Segoe UI", 10))

# Configure grid layout to be responsive
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=0)
root.columnconfigure(2, weight=0)
root.rowconfigure(0, weight=1)

# Chat display
chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Segoe UI", 11), bg="#f4f4f4")
chat_display.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=(10, 5))

# User input
user_input = tk.Entry(root, font=("Segoe UI", 11))
user_input.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")
user_input.bind("<Return>", lambda event: send_message())
root.columnconfigure(0, weight=1)

# Model dropdown
model_selector = ttk.Combobox(root, values=["OpenAI", "Gemini"], state="readonly", width=10)
model_selector.set("OpenAI")
model_selector.grid(row=1, column=1, padx=5, pady=(5, 10))

def get_desktop_path():
    # Return the user's Desktop path on Windows, macOS, or Linux with OneDrive support.
    # Var for OS
    system = platform.system()
    # check for desktop path depending on Operating System, sets paths array for Windows or Linux/macOS
    if system == "Windows":
        user_profile = os.environ.get("USERPROFILE", "")
        paths_to_try = [
            os.path.join(user_profile, "OneDrive", "Desktop"),
            os.path.join(user_profile, "Desktop")
        ]
    else:
        # macOS and Linux
        home = Path.home()
        paths_to_try = [os.path.join(home, "Desktop")]
    # tries to find path for desktop
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    # Fallback to current working directory if Desktop doesn't exist
    return os.getcwd()

# Send button
def send_message():
    # shared variables for chat, message history and AI model
    global chat_session, messages, current_model
    #takes user input, trims it, if prompt is empty, nothing is sent
    prompt = user_input.get().strip()
    if not prompt:
        return
    user_input.delete(0, tk.END)
    # from widget for model selection takes model
    model_choice = model_selector.get()
    current_model = model_choice
    timestamp = datetime.datetime.now().strftime("[%H:%M]")

    # Show user message
    chat_display.config(state='normal')
    chat_display.insert(tk.END, f"{timestamp} You: {prompt}\n")
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)
    chat_log.append(f"{timestamp} You: {prompt}")
    # appends user's input depending on the model, takes model response into reply var, that is added to message queue
    try:
        if model_choice == "OpenAI":
            messages.append({"role": "user", "content": prompt})
            response = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages)
            reply = response.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": reply})
        else:
            if chat_session is None:
                model = genai.GenerativeModel(GOOGLE_MODEL)
                chat_session = model.start_chat()
            response = chat_session.send_message(prompt)
            reply = response.text
    # error handling for exceeding the rate limit or some exceptions
    except openai.error.RateLimitError:
        reply = "❌ OpenAI quota exceeded. Visit https://platform.openai.com/account/usage"
    except ResourceExhausted:
        reply = "❌ Gemini quota exceeded. Visit https://makersuite.google.com/app/apikey"
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    # Show assistant message
    timestamp = datetime.datetime.now().strftime("[%H:%M]")
    chat_display.config(state='normal')
    chat_display.insert(tk.END, f"{timestamp} {model_choice}: {reply}\n\n")
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)
    chat_log.append(f"{timestamp} {model_choice}: {reply}")

send_button = ttk.Button(root, text="Send", command=send_message)
send_button.grid(row=1, column=2, padx=(5, 10), pady=(5, 10))

# Save and exit
def on_closing():
    if chat_log:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{current_model.lower()}_{timestamp}.txt"
        # desktop path for user
        desktop_path = get_desktop_path()
        full_path = os.path.join(desktop_path, filename)
        # tries to save .txt file to desktop path or current working dir; shows success/failure message
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("\n".join(chat_log))
            messagebox.showinfo("Chat Saved", f"Chat log saved to:\n{full_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save chat log:\n{e}")
    root.destroy() # destroys window and exits the app


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
