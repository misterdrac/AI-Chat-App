# LIBRARIES
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog, filedialog
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
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import PyPDF2
import docx
import csv
from fpdf import FPDF
from translations import LANGUAGES, tr


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
theme_mode = "light"
current_lang = "en"

# setting the UI
root = tb.Window(themename="darkly")
root.title("Mister Drac's AI Chatbot")
root.geometry("1080x620")
root.minsize(700, 500)
root.iconbitmap("icon.ico")

# Grid layout configuration
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=0)
root.columnconfigure(2, weight=0)
root.columnconfigure(3, weight=0)
root.rowconfigure(0, weight=1)

# Chat display (tkinter)
chat_frame = tb.Frame(root)
chat_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(10,5))
chat_frame.columnconfigure(0, weight=1)
chat_frame.rowconfigure(0, weight=1)
# Themed Text widget
chat_display = tk.Text(
    chat_frame,
    wrap="word",
    state="disabled",
    font=("Segoe UI", 11),
    bg="#2b2b2b",         # background to match 'darkly'
    fg="#ffffff",         # text color
    insertbackground="#ffffff",  # cursor color
    relief="flat",        # cleaner look
    bd=0
)
chat_display.grid(row=0, column=0, sticky="nsew")

# Scrollbar remains themed
chat_scroll = tb.Scrollbar(
    chat_frame,
    bootstyle="dark",
    orient="vertical",
    command=chat_display.yview
)
chat_scroll.grid(row=0, column=1, sticky="ns")
chat_display.configure(yscrollcommand=chat_scroll.set)

# Entry (ttkbootstrap) - defining dimensions, font, binding for a certain function
user_input = tb.Entry(root, font=("Segoe UI", 11))
user_input.grid(row=2, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")
user_input.bind("<Return>", lambda event: send_message())


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
            reply = response.choices[0].messages.content.strip()
            messages.append({"role": "assistant", "content": reply})
        else:
            if chat_session is None:
                model = genai.GenerativeModel(GOOGLE_MODEL)
                chat_session = model.start_chat()
            response = chat_session.send_message(prompt)
            reply = response.text
    # error handling for exceeding the rate limit or some exceptions
    except openai.error.RateLimitError:
        reply = tr("rate_limit_openai")
    except ResourceExhausted:
        reply = tr("rate_limit_gemini")
    except Exception as e:
        reply = tr("error_prefix").format(e)

    # Show assistant message
    timestamp = datetime.datetime.now().strftime("[%H:%M]")
    chat_display.config(state='normal')
    chat_display.insert(tk.END, f"{timestamp} {model_choice}: {reply}\n\n")
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)
    chat_log.append(f"{timestamp} {model_choice}: {reply}")

# Send button (ttkbootstrap) - defining dimensions and it's text based on current language
send_button = tb.Button(root, text=tr("send", current_lang), bootstyle="success", command=send_message)
send_button.grid(row=2, column=2, padx=(5, 10), pady=(5, 10))

# Model dropdown (ttkbootstrap)
model_selector = tb.Combobox(root, values=["OpenAI", "Gemini"], state="readonly", width=10)
model_selector.set("OpenAI")
model_selector.grid(row=2, column=1, padx=5, pady=(5, 10))

# Upload button logic
def handle_file_upload():
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("CSV files", "*.csv")
        ],
        title="Select a file"
    )
    if not file_path:
        return

    try:
        content = ""
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        elif file_path.endswith(".pdf"):
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
        elif file_path.endswith(".csv"):
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                content = "\n".join([", ".join(row) for row in reader])
        else:
            display_bot_message(tr("error_prefix", current_lang) + " " + tr("unsupported_file", current_lang))
            return

        if not content.strip():
            display_bot_message(tr("file_empty", current_lang))
            return

        action = simpledialog.askstring("Action", tr("file_prompt_action", current_lang))
        if not action or action.lower() not in ("summarize", "translate"):
            display_bot_message(tr("action_cancelled", current_lang))
            return

        short_content = content[:3000]
        if action.lower() == "summarize":
            prompt = f"{tr('summary_header', current_lang)}{short_content}"
        else:
            target_lang = simpledialog.askstring("Translate To", tr("file_prompt_language", current_lang))
            prompt = f"{tr('translate_header', current_lang).format(lang=target_lang)}{short_content}"

        user_input.delete(0, tk.END)
        user_input.insert(0, prompt)
        send_message()

    except Exception as e:
        display_bot_message(tr("messages.file_read_error", current_lang).format(e))

# Upload button
upload_button = tb.Button(root, text=tr("upload", current_lang), bootstyle="secondary", command=handle_file_upload)
upload_button.grid(row=2, column=4, padx=(5, 10), pady=(5, 10))


# Language dropdown (ttkbootstrap)
language_selector = tb.Combobox(root, values=list(LANGUAGES.keys()), state="readonly", width=8)
language_selector.set("en")
language_selector.grid(row=2, column=3, padx=5, pady=(5, 10))

# Language switch callback
def update_language(*args):
    global current_lang
    current_lang = language_selector.get()
    send_button.config(text=tr("send", current_lang))
    upload_button.config(text=tr("upload", current_lang))
    language_selector.config(values=list(LANGUAGES.keys()))
language_selector.bind("<<ComboboxSelected>>", update_language)

def get_desktop_path():
    # Return the user's Desktop path on Windows, macOS, or Linux with OneDrive support.
    # Var for OS
    system = platform.system()
    # check for desktop path depending on Operating System, sets paths array for Windows or Linux/macOS
    if system == "Windows":
        user_profile = os.environ.get("USERPROFILE", "")
        candidates = [
            Path(user_profile) / "OneDrive" / "Desktop",
            Path(user_profile) / "Desktop"
        ]
    else:
        candidates = [ Path.home() / "Desktop" ]

    for p in candidates:
        if p.exists():
            return p
    # fallback to cwd
    return Path.cwd()

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
        # Grab the per-language commands map (or fall back to English)
        cmds = LANGUAGES.get(current_lang, {}).get("commands")
        if not isinstance(cmds, dict):
            cmds = LANGUAGES["en"]["commands"]

        # Build each line: "/foo — localized description"
        lines = [f"{cmd} — {desc}" for cmd, desc in cmds.items()]

        # Join them and display under the localized header
        help_body = "\n".join(lines)
        display_bot_message(f"{tr('help_header', current_lang)}\n{help_body}")
        return

    elif cmd_lower == "/clear":
        chat_display.config(state='normal')
        chat_display.delete('1.0', tk.END)
        chat_display.config(state='disabled')
        chat_log.clear()
        display_bot_message(tr("messages.chat_cleared", current_lang))

    elif cmd_lower == "/exit":
        root.quit()

    elif cmd_lower == "/model":
        display_bot_message(tr("messages.current_model", current_lang).format(current_model))

    elif cmd_lower == "/switch":
        model_selector.set("Gemini" if current_model == "OpenAI" else "OpenAI")
        current_model = model_selector.get()
        display_bot_message(tr("messages.switched_model", current_lang).format(current_model))

    elif cmd_lower == "/stats":
        display_bot_message(tr("messages.messages_exchanged", current_lang).format(len(chat_log)))

    elif cmd_lower == "/feedback":
        display_bot_message(tr("messages.feedback", current_lang))

    elif cmd_lower == "/theme":
        toggle_theme()

    elif cmd_lower == "/copylast":
        if chat_log:
            root.clipboard_clear()
            root.clipboard_append(chat_log[-1])
            display_bot_message(tr("messages.copied", current_lang))
        else:
            display_bot_message(tr("messages.nothing_to_copy", current_lang))

    elif cmd_lower == "/save":
        filename = simpledialog.askstring("Save As", "It will be saved as .txt, Enter custom filename:")
        if filename:
            filename = filename.strip().replace(" ", "_") + ".txt"
            path = get_desktop_path() / filename
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(chat_log))
                last_saved_file = path
                display_bot_message(tr("messages.chat_saved_as", current_lang).format(filename))
            except Exception as e:
                display_bot_message(tr("messages.chat_save_failed", current_lang).format(str(e)))

    elif cmd_lower == "/history":
        user_messages = [line for line in chat_log if line.strip().endswith(":") is False and user_name in line]
        display_bot_message(tr("messages.last_messages", current_lang) + "\n".join(user_messages[-5:]))

    elif cmd_lower == "/version":
        display_bot_message(tr("messages.version", current_lang))

    elif cmd_lower == "/timestamp":
        timestamps_enabled = not timestamps_enabled
        display_bot_message(tr("messages.timestamps_on", current_lang) if timestamps_enabled else tr("messages.timestamps_off"))

    elif cmd_lower == "/reset":
        messages.clear()
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        chat_session = None
        display_bot_message(tr("messages.context_reset", current_lang))

    elif cmd_lower == "/deletefile":
        if last_saved_file and last_saved_file.exists():
            try:
                last_saved_file.unlink()
                display_bot_message(tr("messages.file_deleted", current_lang).format(last_saved_file.name))
            except Exception as e:
                display_bot_message(tr("messages.file_delete_failed", current_lang).format(e))
        else:
            display_bot_message(tr("messages.no_file_to_delete", current_lang))

    elif cmd_lower == "/openlog":
        os.startfile(get_desktop_path()) if os.name == 'nt' else os.system(f'open "{get_desktop_path()}"')

    elif cmd_lower == "/exportjson":
        json_file = get_desktop_path() / f"chat_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(chat_log, f, indent=2)
            display_bot_message(tr("messages.json_exported", current_lang).format(json_file.name))
        except Exception as e:
            display_bot_message(tr("messages.json_export_failed", current_lang).format(str(e)))

    elif cmd_lower == "/exportpdf":
        export_chat_to_pdf()

    elif cmd_lower == "/openaiusage":
        webbrowser.open("https://platform.openai.com/account/usage")

    elif cmd_lower == "/geminiusagelink":
        webbrowser.open("https://makersuite.google.com/app/apikey")

    elif cmd_lower == "/setname":
        new_name = simpledialog.askstring("Set Name", "Enter your name:")
        if new_name:
            user_name = new_name
            display_bot_message(tr("messages.name_set", current_lang).format(user_name))

    elif cmd_lower == "/emoji":
        emoji_list = "😀 😎 🤖 🧠 💬 ✅ ❌ 💡 🔁 📝"
        display_bot_message(tr("messages.emoji_list", current_lang).format(emoji_list))

    elif cmd_lower == "/shrink":
        if len(chat_log) < 4:
            display_bot_message(tr("messages.not_enough_to_summarize", current_lang))
        else:
            try:
                summary_prompt = "Summarize the following conversation:\n\n" + "\n".join(chat_log[-10:])
                if current_model == "OpenAI":
                    summary_response = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": summary_prompt}]
                    )
                    summary = summary_response.choices[0].messages.content.strip()
                else:
                    if chat_session is None:
                        model = genai.GenerativeModel(GOOGLE_MODEL)
                        chat_session = model.start_chat()
                    summary_response = chat_session.send_message(summary_prompt)
                    summary = summary_response.text
                display_bot_message(tr("messages.summary_result", current_lang) + summary)
            except Exception as e:
                display_bot_message(tr("messages.summary_failed", current_lang).format(e))

    elif cmd_lower.startswith("/translate"):
        # Default to English if no language is specified
        parts = cmd_lower.split(" ")
        lang = parts[1] if len(parts) > 1 else "en"

        # Find last assistant message
        last_response = next((msg for msg in reversed(chat_log) if current_model in msg), None)
        if not last_response:
            display_bot_message(tr("messages.no_response_to_translate", current_lang))
        else:
            try:
                translate_prompt = f"Translate this into {lang}:\n{last_response}"
                if current_model == "OpenAI":
                    translation = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": translate_prompt}]
                    ).choices[0].messages.content.strip()
                else:
                    if chat_session is None:
                        model = genai.GenerativeModel(GOOGLE_MODEL)
                        chat_session = model.start_chat()
                    translation = chat_session.send_message(translate_prompt).text

                    display_bot_message(tr("messages.translation_result", current_lang).format(lang, translation))
            except Exception as e:
                display_bot_message(tr("messages.translation_failed", current_lang))

    else:
        # Suggestions for partial command
        filtered = [cmd for cmd in COMMANDS if cmd.startswith(cmd_lower)]
        if filtered:
            display_bot_message(tr("did_you_mean", current_lang) + "\n".join(filtered))
        else:
            display_bot_message(tr("unknown_command", current_lang))

def display_bot_message(text):
    timestamp = datetime.datetime.now().strftime("[%H:%M]")
    chat_display.config(state='normal')
    chat_display.insert(tk.END, f"{timestamp} System: {text}\n\n")
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)
    chat_log.append(f"{timestamp} System: {text}")

# for /theme command
themes = ["darkly", "flatly", "cyborg", "minty", "solar", "superhero", "cosmo", "lumen", "pulse", "sandstone", "united", "yeti",
          "morph", "simplex", "cerculean", "vapor", "litera"]
current_theme_index = 0
def toggle_theme():
    global current_theme_index
    current_theme_index = (current_theme_index + 1) % len(themes)
    new_theme = themes[current_theme_index]
    root.style.theme_use(new_theme)
    display_bot_message(tr("messages.theme", current_lang).format(new_theme))

# for /exportpdf command
def export_chat_to_pdf():
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{timestamp}.pdf"
        desktop = get_desktop_path()           # this now returns a Path
        desktop.mkdir(parents=True, exist_ok=True)
        full_path: Path = desktop / filename

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in chat_log:
            # replace characters that Latin-1 can't encode
            safe_line = line.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 10, safe_line)

        pdf.output(str(full_path))
        display_bot_message(tr("messages.pdf_export_success", current_lang).format(filename))
    except Exception as e:
        display_bot_message(tr("messages.pdf_export_failed", current_lang).format(e))

# Save and exit
def on_closing():
    root.destroy() # destroys window and exits the app

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()