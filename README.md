# Mister Drac’s AI Chatbot

A desktop GUI chat application powered by OpenAI’s GPT-4 and Google Gemini, with multilingual UI, file-upload processing, PDF export,
theming, and image-generation support (with built-in API-failover to Hugging Face). Image generation is buggy....

---

## 🚀 Features

- **Dual-engine chat**: choose between OpenAI (GPT-4) and Google Gemini.
- **Multilingual UI**: dynamic text via `translations.py`—supports dot-notation keys, per-language command descriptions, and fallback to English.
- **Slash-commands**:
    - `/help` — localized list of all commands
    - `/save` — save chat log (.txt) to your Desktop
    - `/exportjson`, `/exportpdf` — export history as JSON or styled PDF
    - `/clear`, `/reset`, …and many more
- **File upload & processing**: select `.txt`, `.pdf`, `.docx`, `.csv` → summarize or translate content.
- **Image generation**: “Generate Image” button uses OpenAI’s Image API, automatically falls back to Hugging Face’s Stable Diffusion on error.
- **Custom theming**: toggle through a dozen+ TTK Bootstrap themes on-the-fly.
- **Timestamps, custom username & stats**: enable/disable timestamps, set your display name, view message counters.

---

## 📋 Requirements

- Python 3.9+
- OpenAI API key (`OPENAI_API_KEY` in `.env`)
- Google Gemini API key (`GOOGLE_API_KEY` in `.env`)
- (Optional) Hugging Face token (`HF_API_KEY` in `.env`) for image fallback
- Dependencies:
  ```bash
  pip install ttkbootstrap openai google-generativeai huggingface_hub PyPDF2 python-docx fpdf2 python-dotenv

---

## ⚙️ Configuration

1. inside your **.env** file, enter your API keys
2. **(Optional)** extend or tweek language translations or add your own translations if you wish, in `translations.py` file

---

## ▶️ How to run the app?

- inside your working directory where `app.py` is located, type:
  ```cmd
    python app.py

---

## 📚 Built-in Commands
|Command|Description|
|-------|-----------|
|/help| Show all localized commands|
|/save| Save chatlog to Desktop|
|/exportpdf| Export chatlog as .pdf file|
|/exportjson| Export chatlog as .json file|
|/clear| Clears window of chat and history|
|/reset| Resets AI conversation context|
|/model| Displays which AI model user is using|
|/switch| Switches between AI models|
|/stats| Show number of exchanged messages|
|/theme| Changes theme of a window|
|/copylast| Copies last response from AI to user's clipboard|
|/translate| Translates last response to desired language|
|/emoji| Shows list of available emojis|
|...and more!| See `/help` for the full list|

---

# 🗂️ File processing

- **Translate** or **summarize** any uploaded `.txt`, `.pdf`, `.docx` or `.csv` file, just hit upload button 
  and that's it, you will get output in chat

---

# 🙋🏼‍♂️ Author
- This project is created by **`Dario Golubović`**

---

# 💭 Why I created this?

I was thinking about what to create, then I just got this idea, experimented with this. Programming in Python
seems simple enough sometimes, but sometimes I forget how fast you can build a desktop app with Python in a such
short period of time. I just wanted to see how this creating chat with AI works, how to implement certain features. 
Project was more of experiment, I just tinkered with stuff, I believe this can be something more greater, but myself 
currently lacks will to continue this