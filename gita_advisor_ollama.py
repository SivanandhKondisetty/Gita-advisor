"""
GITA ADVISOR — KARMAN-EVADHIKAARSTHE
उद्धरेदात्मनात्मानम् — Elevate yourself through the Self alone.
 
Features:
  - Persistent journal saved to gita_journal.txt (same folder as this file)
  - Conversation memory within session + last 5 exchanges from previous sessions
  - Strict Gita-only responses. No sugarcoating. Only dharma.
  - Runs completely FREE and OFFLINE using local Mistral model via Ollama
 
Setup:
    1. Install Ollama from https://ollama.ai/download
    2. Run: ollama pull mistral
    3. Run: pip install ollama
    4. Run: python gita_advisor.py
 
No API key needed. No internet needed. No cost. Ever.
"""
 
import os
import sys
import json
import textwrap
from datetime import datetime
from pathlib import Path
 
# ── dependency check ──────────────────────────────────────────────────────────
try:
    import ollama
except ImportError:
    print("\n[ERROR] 'ollama' package not found.")
    print("Run:  pip install ollama\n")
    sys.exit(1)
 
 
# ── paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
JOURNAL_TXT = BASE_DIR / "gita_journal.txt"
MEMORY_JSON = BASE_DIR / "gita_memory.json"
 
 
# ── system prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a strict, direct Bhagavad Gita advisor. No flattery. No comfort. Only dharma.
 
You will be given:
1. A summary of past conversations (if any) — use this to understand the person's ongoing struggles and patterns.
2. The current conversation so far this session.
3. The user's latest situation or question.
 
Use the past context to give more precise, personalized advice.
If you see a repeating pattern (same struggle appearing again), name it directly and address it.
 
Respond with EXACTLY this structure and nothing else:

--- SLOKA ---
[Sanskrit sloka — original text]
Reference: Chapter [X], Verse [Y]

--- MEANING ---
[Plain English meaning in 2-3 sentences. Simple. No jargon.]

--- DHARMA FOR YOUR SITUATION ---
[3-5 direct, practical instructions applied to this exact situation.
No sugarcoating. No pity. Speak as Krishna to Arjuna.
Use "you" directly. Tell them what to DO and what to STOP.]
[Sanskrit sloka — original text]
 
Reference: Chapter [X], Verse [Y]

 
Rules:
- Always pick the most relevant sloka, not the most famous one.
- If the situation involves attachment, use Nishkama Karma or Anasakti references.
- If the situation involves fear or procrastination, use duty/courage references.
- If the situation involves ego or pride, use the Atman references.
- If the same struggle has appeared in past context, address the pattern directly.
- Never say "I understand your pain." Never soften the advice.
- The advice must feel like it was written specifically for this person's situation."""
 
 
# ── memory helpers ────────────────────────────────────────────────────────────
def load_memory() -> list:
    """Load past conversation exchanges from memory file."""
    if not MEMORY_JSON.exists():
        return []
    try:
        with open(MEMORY_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
 
 
def save_memory(memory: list):
    """Save last 20 exchanges to memory file."""
    trimmed = memory[-20:]
    with open(MEMORY_JSON, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)
 
 
def build_past_context(memory: list) -> str:
    """Build a short summary of past exchanges to inject into first message."""
    if not memory:
        return ""
    lines = ["PAST CONVERSATION CONTEXT (from previous sessions):"]
    for i, entry in enumerate(memory[-5:], 1):
        lines.append(f"\n[Past Exchange {i}]")
        lines.append(f"Situation: {entry['situation'][:300]}")
        lines.append(f"Advice given: {entry['response'][:400]}")
    return "\n".join(lines)
 
 
# ── journal helper ────────────────────────────────────────────────────────────
def append_to_journal(situation: str, response: str):
    """Append a Q&A pair to the human-readable journal file."""
    timestamp = datetime.now().strftime("%d %B %Y, %I:%M %p")
    divider   = "═" * 60
    entry = f"""
{divider}
  {timestamp}
{divider}
 
YOUR SITUATION:
{situation}
 
{response}
 
"""
    with open(JOURNAL_TXT, "a", encoding="utf-8") as f:
        f.write(entry)
 
 
# ── display helpers ───────────────────────────────────────────────────────────
def print_banner():
    print(r"""
  ╔══════════════════════════════════════════════════════════╗
  ║           GITA ADVISOR — उद्धरेदात्मनात्मानम्           ║
  ║         "Elevate yourself through the Self alone."       ║
  ║              Powered by Local Mistral — Free Forever     ║
  ╚══════════════════════════════════════════════════════════╝
""")
 
 
def print_commands():
    print("  Commands:")
    print("  'history'  — view exchanges so far this session")
    print("  'journal'  — see where your journal file is saved")
    print("  'clear'    — clear screen, keep memory, fresh session")
    print("  'quit'     — save and exit\n")
 
 
def wrap_output(text: str, width: int = 70) -> str:
    lines   = text.split("\n")
    wrapped = []
    for line in lines:
        if len(line) > width and not line.startswith("━") and not line.startswith("═"):
            wrapped.append(textwrap.fill(line, width=width))
        else:
            wrapped.append(line)
    return "\n".join(wrapped)
 
 
# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print_banner()
    print_commands()
 
    print("  Connecting to local Mistral model...\n")
 
    # load persistent memory from all previous sessions
    memory       = load_memory()
    past_context = build_past_context(memory)
 
    if memory:
        print(f"  Memory loaded — {len(memory)} past exchange(s) remembered.\n")
    else:
        print("  No past sessions found. Starting fresh.\n")
 
    session_history = []
    first_message   = True
 
    while True:
        try:
            print("─" * 60)
            situation = input("  Your situation: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Saving session... Jai Shri Krishna.\n")
            save_memory(memory)
            break
 
        if not situation:
            continue
 
        # ── commands ──────────────────────────────────────────────────────────
        if situation.lower() in ("quit", "exit"):
            print("\n  Saving session... Jai Shri Krishna.\n")
            save_memory(memory)
            break
 
        if situation.lower() == "clear":
            session_history.clear()
            first_message = True
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()
            print_commands()
            if memory:
                print(f"  Memory active — {len(memory)} past exchange(s) remembered.\n")
            continue
 
        if situation.lower() == "history":
            count = len(session_history) // 2
            if count == 0:
                print("\n  No exchanges yet this session.\n")
            else:
                print(f"\n  {count} exchange(s) this session:\n")
                for msg in session_history:
                    if msg["role"] == "user":
                        preview = msg["content"][:120].replace("\n", " ")
                        print(f"  You: {preview}...")
                print()
            continue
 
        if situation.lower() == "journal":
            print(f"\n  Journal file location:\n  {JOURNAL_TXT.resolve()}\n")
            continue
 
        # ── build message list ─────────────────────────────────────────────
        if first_message and past_context:
            user_content  = f"{past_context}\n\n---\nCURRENT SITUATION:\n{situation}"
            first_message = False
        else:
            user_content  = situation
            first_message = False
 
        messages_to_send = list(session_history)
        messages_to_send.append({"role": "user", "content": user_content})
 
        print("\n  Seeking wisdom from the Gita...\n")
 
        try:
            messages_with_system = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + messages_to_send
            api_response  = ollama.chat(
            model="mistral",
            #model="phi3:mini",
            messages=messages_with_system,
            options={"num_predict": 1024}
           )
            response_text = api_response['message']['content']
            #response_text = api_response.message.content
            #print(f"DEBUG: {repr(response_text[:200])}")  # temporary debug line
            response_text = api_response.message.content
            print(f"LENGTH: {len(response_text)}")
            print(f"CONTENT: {response_text[:500]}")
            session_history.append({"role": "user",      "content": situation})
            session_history.append({"role": "assistant", "content": response_text})
 
            memory.append({"situation": situation, "response": response_text})
            append_to_journal(situation, response_text)
 
            print(wrap_output(response_text))
            print(f"\n  Saved to journal.\n")
 
        except ollama.ResponseError as e:
            print(f"\n[ERROR] Ollama model error: {e}\n")
        except ConnectionError:
            print("\n[ERROR] Ollama not running. Run 'ollama serve' in a separate terminal.\n")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}\n")
 
 
if __name__ == "__main__":
    main()
