"""
Rule-based commands. Each handler takes the lowercased user text and
returns a spoken reply, or None if that handler doesn't apply.


Add your own by writing a function with the same signature and
registering it in HANDLERS at the bottom of the file.
"""

import datetime
import random
import webbrowser

import requests

from voice_assistant import config


EXIT_WORDS = {"quit", "exit", "stop", "goodbye", "bye", "shut down", "shutdown", "power off", "turn off"}



def handle_exit(text: str):
    if any(word in text for word in EXIT_WORDS):
        return "Goodbye!"
    return None


def handle_greeting(text: str):
    if any(g in text for g in ("hello", "hi ", "hi,", "hey")) or text.strip() in (
        "hi",
        "hey",
    ):
        return random.choice(
            ["Hello! How can I help?", "Hey there!", "Hi! What can I do for you?"]
        )
    return None


def handle_time(text: str):
    if "time" in text:
        now = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
        return f"It's {now} right now."
    return None


def handle_weather(text: str):
    """Best-effort weather stub.

    Without an external weather API, we respond with a friendly fallback.
    You can later wire this to a real service.
    """
    if "weather" in text:
        # Optional simple location extraction: "weather in X"
        # If not present, just give a generic response.
        loc = None
        if "weather in" in text:
            loc = text.split("weather in", 1)[1].strip()
        if loc:
            return f"Weather in {loc}: I can't fetch live weather right now, but it feels like a typical day."
        return "I can't fetch live weather right now, but it looks like a good day."
    return None



def handle_date(text: str):
    if "date" in text or "day is it" in text:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."
    return None


def handle_name(text: str):
    # Identify assistant
    if "your name" in text or "who are you" in text:
        return f"I'm {config.ASSISTANT_NAME}, your voice assistant."

    # Identify user (optional)
    if "my name is" in text or "i am" in text or "i'm" in text or "name is" in text:
        return "Nice to meet you, Brijesh Guleria."

    # Also handle: what is my name
    if "what is my name" in text or "my name" in text:
        return "Your name is Brijesh Guleria."

    # Branch/degree (best-effort)
    if "branch" in text and "b tech" in text and "ece" in text:
        return "B.Tech ECE, Branch B."

    # College/collage name (best-effort)
    if (
        "collage name" in text
        or "college name" in text
        or "my collage name" in text
        or "my college name" in text
    ):
        return "C.G.C. University."

    if "cgc university" in text:
        return "C.G.C. University."

    return None




def handle_joke(text: str):
    if "joke" in text:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything.",
            "I told my computer I needed a break, and it said no problem, "
            "it'll go to sleep.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
        ]
        return random.choice(jokes)
    return None


def handle_open_website(text: str):
    # Supports both:
    # - "open youtube"
    # - "open spotify"
    sites = {
        "youtube": "https://youtube.com",
        "spotify": "https://open.spotify.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "wikipedia": "https://wikipedia.org",
        "github": "https://github.com",
    }

    # For safety, only open when user explicitly says "open ...".
    if text.startswith("open ") or "open " in text:
        for name, url in sites.items():
            if name in text:
                webbrowser.open(url)
                return f"Opening {name}."
    return None




def handle_wikipedia(text: str):
    trigger = None
    for phrase in ("who is", "what is", "tell me about", "search wikipedia for"):
        if phrase in text:
            trigger = phrase
            break
    if not trigger:
        return None

    query = text.split(trigger, 1)[1].strip()
    if not query:
        return None

    try:
        resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}",
            timeout=5,
        )
        if resp.status_code == 200:
            summary = resp.json().get("extract")
            if summary:
                # Keep it short for speech.
                sentences = summary.split(". ")
                return ". ".join(sentences[:2]).rstrip(".") + "."
        return f"I couldn't find a Wikipedia summary for {query}."
    except requests.RequestException:
        return "I couldn't reach Wikipedia right now."


# Order matters: first handler that returns a non-None reply wins.
HANDLERS = [
    handle_exit,
    handle_greeting,
    handle_time,
    handle_weather,
    handle_date,
    handle_name,
    handle_joke,
    handle_open_website,
    handle_wikipedia,
]



def handle(text: str):
    """Try each rule-based handler. Returns a reply string, or None if
    no rule matched (caller should fall back to the LLM)."""
    lowered = text.lower().strip()
    for handler in HANDLERS:
        reply = handler(lowered)
        if reply is not None:
            return reply
    return None
