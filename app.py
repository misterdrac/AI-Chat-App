# LIBRARIES
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import os
import datetime
import platform
from pathlib import Path
import webbrowser
import json
import shutil

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
last_saved_file = None  # Store last saved filename
timestamps_enabled = True
user_name = "You"

# setting the UI
root = tk.Tk()
root.title("Mister Drac's AI Chatbot")
root.geometry("1080x620")
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

# Commands list
COMMANDS = {
    "/help": "Show available commands",
    "/save": "Manually save the chat to desktop",
    "/clear": "Clear chat history and screen",
    "/exit": "Exit the application",
    "/model": "Show current active model",
    "/switch": "Switch between OpenAI and Gemini",
    "/stats": "Show usage stats",
    "/feedback": "Write feedback to developer",
    "/theme": "Toggle theme (if supported)",
    "/copylast": "Copy last response",
    "/saveas": "Save chat log with custom filename",
    "/history": "Show recent user messages",
    "/version": "Show app version",
    "/timestamp": "Toggle timestamps on/off in chat view",
    "/reset": "Reset the AI context/session",
    "/deletefile": "Delete the last saved .txt file",
    "/openlog": "Open the folder containing saved logs",
    "/exportjson": "Export chat history as JSON",
    "/openaiusage": "Open OpenAI usage dashboard in browser",
    "/geminiusagelink": "Open Gemini API key dashboard",
    "/setname": "Set your display name in chat",
    "/emoji": "Insert common emojis",
    "/shrink": "Collapse chat history to summary (if supported)",
    "/translate": "Translate last response to selected language",
}



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

# handling commands
def handle_command(cmd):
    global current_model, chat_log, messages, chat_session, timestamps_enabled, user_name, last_saved_file

    timestamp = datetime.datetime.now().strftime("[%H:%M]") if timestamps_enabled else ""
    cmd_lower = cmd.lower().strip()

    # Display user's command in chat
    chat_display.config(state='normal')
    chat_display.insert(tk.END, f"{timestamp} {user_name}: {cmd}\n")
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)

    if cmd_lower == "/help":
        help_text = "\n".join([f"{k} — {v}" for k, v in COMMANDS.items()])
        display_bot_message("📖 Available commands:\n" + help_text)

    elif cmd_lower == "/clear":
        chat_display.config(state='normal')
        chat_display.delete('1.0', tk.END)
        chat_display.config(state='disabled')
        chat_log.clear()
        display_bot_message("🧹 Chat cleared.")

    elif cmd_lower == "/save":
        manual_save()

    elif cmd_lower == "/exit":
        root.quit()

    elif cmd_lower == "/model":
        display_bot_message(f"🤖 Current model: {current_model}")

    elif cmd_lower == "/switch":
        model_selector.set("Gemini" if current_model == "OpenAI" else "OpenAI")
        current_model = model_selector.get()
        display_bot_message(f"🔁 Switched to {current_model}")

    elif cmd_lower == "/stats":
        display_bot_message(f"📊 Messages exchanged: {len(chat_log)}")

    elif cmd_lower == "/feedback":
        display_bot_message("💬 Send your feedback to: dev@yourdomain.com")

    elif cmd_lower == "/theme":
        display_bot_message("🎨 Theme toggling is not implemented yet.")

    elif cmd_lower == "/copylast":
        if chat_log:
            root.clipboard_clear()
            root.clipboard_append(chat_log[-1])
            display_bot_message("✅ Last response copied to clipboard.")
        else:
            display_bot_message("⚠️ Nothing to copy.")

    elif cmd_lower == "/saveas":
        filename = simpledialog.askstring("Save As", "Enter custom filename:")
        if filename:
            filename = filename.strip().replace(" ", "_") + ".txt"
            path = get_desktop_path() / filename
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(chat_log))
                last_saved_file = path
                display_bot_message(f"✅ Chat saved as '{filename}'")
            except Exception as e:
                display_bot_message(f"❌ Failed to save: {str(e)}")

    elif cmd_lower == "/history":
        user_messages = [line for line in chat_log if line.strip().endswith(":") is False and user_name in line]
        display_bot_message("📜 Last messages:\n" + "\n".join(user_messages[-5:]))

    elif cmd_lower == "/version":
        display_bot_message("📦 Version 1.0.0")

    elif cmd_lower == "/timestamp":
        timestamps_enabled = not timestamps_enabled
        display_bot_message(f"⏱️ Timestamps {'enabled' if timestamps_enabled else 'disabled'}.")

    elif cmd_lower == "/reset":
        messages.clear()
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        chat_session = None
        display_bot_message("🔄 AI context reset.")

    elif cmd_lower == "/deletefile":
        if last_saved_file and last_saved_file.exists():
            try:
                last_saved_file.unlink()
                display_bot_message(f"🗑️ Deleted {last_saved_file.name}")
            except Exception as e:
                display_bot_message(f"❌ Failed to delete file: {e}")
        else:
            display_bot_message("⚠️ No saved file to delete.")

    elif cmd_lower == "/openlog":
        os.startfile(get_desktop_path()) if os.name == 'nt' else os.system(f'open "{get_desktop_path()}"')

    elif cmd_lower == "/exportjson":
        json_file = get_desktop_path() / f"chat_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(chat_log, f, indent=2)
            display_bot_message(f"🗃️ Exported chat as JSON:\n{json_file.name}")
        except Exception as e:
            display_bot_message(f"❌ Export failed: {str(e)}")

    elif cmd_lower == "/openaiusage":
        webbrowser.open("https://platform.openai.com/account/usage")

    elif cmd_lower == "/geminiusagelink":
        webbrowser.open("https://makersuite.google.com/app/apikey")

    elif cmd_lower == "/setname":
        new_name = simpledialog.askstring("Set Name", "Enter your name:")
        if new_name:
            user_name = new_name
            display_bot_message(f"🙋 Your name is now: {user_name}")

    elif cmd_lower == "/emoji":
        emoji_list = "😀 😎 🤖 🧠 💬 ✅ ❌ 💡 🔁 📝"
        display_bot_message("💬 Emojis you can use:\n" + emoji_list)

    elif cmd_lower == "/shrink":
        if len(chat_log) < 4:
            display_bot_message("🧠 Not enough content to summarize.")
        else:
            try:
                summary_prompt = "Summarize the following conversation:\n\n" + "\n".join(chat_log[-10:])
                if current_model == "OpenAI":
                    summary_response = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": summary_prompt}]
                    )
                    summary = summary_response.choices[0].message.content.strip()
                else:
                    if chat_session is None:
                        model = genai.GenerativeModel(GOOGLE_MODEL)
                        chat_session = model.start_chat()
                    summary_response = chat_session.send_message(summary_prompt)
                    summary = summary_response.text
                display_bot_message("🧠 Summary:\n" + summary)
            except Exception as e:
                display_bot_message(f"❌ Summarization failed: {e}")

    elif cmd_lower.startswith("/translate"):
        # Default to English if no language is specified
        parts = cmd_lower.split(" ")
        lang = parts[1] if len(parts) > 1 else "en"

        # Find last assistant message
        last_response = next((msg for msg in reversed(chat_log) if current_model in msg), None)
        if not last_response:
            display_bot_message("🌐 No assistant response found to translate.")
        else:
            try:
                translate_prompt = f"Translate this into {lang}:\n{last_response}"
                if current_model == "OpenAI":
                    translation = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": translate_prompt}]
                    ).choices[0].message.content.strip()
                else:
                    if chat_session is None:
                        model = genai.GenerativeModel(GOOGLE_MODEL)
                        chat_session = model.start_chat()
                    translation = chat_session.send_message(translate_prompt).text

                display_bot_message(f"🌐 Translation ({lang}):\n{translation}")
            except Exception as e:
                display_bot_message(f"❌ Translation failed: {e}")


    elif cmd_lower == "/":
            suggestions = "\n".join(COMMANDS.keys())
            display_bot_message("📘 All commands:\n" + suggestions)

    else:
        # Suggestions for partial command
        filtered = [cmd for cmd in COMMANDS if cmd.startswith(cmd_lower)]
        if filtered:
            display_bot_message("🤔 Did you mean:\n" + "\n".join(filtered))
        else:
            display_bot_message("❓ Unknown command. Type /help to see available commands.")

def display_bot_message(text):
    timestamp = datetime.datetime.now().strftime("[%H:%M]")
    chat_display.config(state='normal')
    chat_display.insert(tk.END, f"{timestamp} System: {text}\n\n")
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)
    chat_log.append(f"{timestamp} System: {text}")

def manual_save():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_log_{current_model.lower()}_{timestamp}.txt"
    desktop_path = get_desktop_path()
    full_path = os.path.join(desktop_path, filename)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("\n".join(chat_log))
        messagebox.showinfo("Chat Saved", f"Chat log saved to:\n{full_path}")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save chat log:\n{e}")


# Send button
def send_message():
    # shared variables for chat, message history and AI model
    global chat_session, messages, current_model
    #takes user input, trims it, if prompt is empty, nothing is sent
    prompt = user_input.get().strip()
    if not prompt:
        return
    user_input.delete(0, tk.END)
    # for prompting commands
    if prompt.startswith("/"):
        handle_command(prompt)
        return
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
