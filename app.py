import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import openai
from dotenv import load_dotenv
import os
import datetime
import ctypes.wintypes
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

# Setup Rich console
console = Console()

# return desktop path
def get_windows_desktop_path():
    CSIDL_DESKTOP = 0x0000
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value

# Load .env variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GOOGLE_MODEL = "gemini-2.5-flash"
OPENAI_MODEL = "gpt-4o"

genai.configure(api_key=GOOGLE_API_KEY)
openai.api_key = OPENAI_API_KEY

chat_log = []

# Model Selection Prompt
console.print("[bold magenta]Choose your AI model:[/bold magenta]")
console.print("[cyan]1.[/cyan] OpenAI ChatGPT")
console.print("[cyan]2.[/cyan] Google Gemini")
choice = Prompt.ask("[bold green]Enter 1 or 2[/bold green]")

if choice == '1':
    console.print("\n[bold blue]Chat with OpenAI GPT-4o — type 'stop' to exit.[/bold blue]")
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    while True:
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        if user_input.lower() == 'stop':
            break
        if not user_input:
            console.print("[yellow]⚠️ Input cannot be empty.[/yellow]")
            continue

        messages.append({"role": "user", "content": user_input})
        chat_log.append(f"You: {user_input}")

        try:
            response = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages)
            reply = response.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": reply})
            chat_log.append(f"GPT-4o: {reply}")
            console.print(Panel(reply, title="GPT-4o", border_style="green", box=box.ROUNDED))

        except openai.error.RateLimitError:
            console.print(Panel.fit(
                "[bold red]❌ You’ve run out of OpenAI usage today or exceeded your quota.[/bold red]\n"
                "[blue]Visit https://platform.openai.com/account/usage to check your usage.[/blue]",
                title="Rate Limit Exceeded",
                border_style="red"
            ))
            break

elif choice == '2':
    model = genai.GenerativeModel(GOOGLE_MODEL)
    chat_session = model.start_chat()

    console.print(f"\n[bold blue]Chat with Google Gemini ({GOOGLE_MODEL}) — type 'stop' to exit.[/bold blue]")
    while True:
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        if user_input.lower() == "stop":
            break
        if not user_input:
            console.print("[yellow]⚠️ Input cannot be empty. Try again.[/yellow]")
            continue

        chat_log.append(f"You: {user_input}")

        try:
            response = chat_session.send_message(user_input)
            reply = response.text
            chat_log.append(f"Gemini: {reply}")
            console.print(Panel(reply, title="Gemini", border_style="bright_blue", box=box.ROUNDED))

        except ResourceExhausted:
            console.print(Panel.fit(
                "[bold red]❌ You’ve hit your Gemini API quota.[/bold red]\n"
                "[blue]Visit https://makersuite.google.com/app/apikey to check usage.[/blue]",
                title="Rate Limit Exceeded",
                border_style="red"
            ))
            break

        except Exception as e:
            console.print(f"[red]❌ Error:[/red] {str(e)}")
            break

else:
    console.print("[red]Invalid choice. Exiting...[/red]")

# Save chat log to desktop
if chat_log:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_log_{'openai' if choice == '1' else 'gemini'}_{timestamp}.txt"

    desktop_path = get_windows_desktop_path()
    if not os.path.exists(desktop_path):
        desktop_path = "."

    full_path = os.path.join(desktop_path, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chat_log))

    console.print(Panel.fit(
        f"📝 Chat log saved to [bold green]{full_path}[/bold green]",
        title="Saved",
        border_style="green"
    ))

    # Auto-open the file on Windows
    try:
        os.startfile(full_path)
    except Exception as e:
        console.print(f"[yellow]⚠️ Couldn't open file automatically: {e}[/yellow]")
