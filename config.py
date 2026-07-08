"""
Central configuration for the voice assistant.

Environment variables (optional):
    ANTHROPIC_API_KEY   - set this to enable smart LLM fallback answers.
    ASSISTANT_NAME      - what the assistant calls itself. Default: "Jarvis".
    TTS_RATE            - speech rate (words/min) for text-to-speech. Default: 175.
    TTS_VOLUME          - 0.0 to 1.0. Default: 1.0.
    STT_LANGUAGE        - language code for speech recognition. Default: "en-US".
"""

import os

ASSISTANT_NAME = os.environ.get("ASSISTANT_NAME", "Jarvis")

# --- Text to speech ---
TTS_RATE = int(os.environ.get("TTS_RATE", "175"))
TTS_VOLUME = float(os.environ.get("TTS_VOLUME", "1.0"))
# Leave blank to use the system default voice. Run `list_voices.py`
# (see README) to see what's available on your machine, then paste
# the voice id here if you want a specific one.
TTS_VOICE_ID = os.environ.get("TTS_VOICE_ID", "")

# --- Speech to text ---
STT_LANGUAGE = os.environ.get("STT_LANGUAGE", "en-US")
# How long (seconds) to wait for the person to start talking before giving up.
STT_TIMEOUT = 6
# How long (seconds) a single utterance is allowed to run before we stop listening.
STT_PHRASE_TIME_LIMIT = 15

# --- LLM fallback (optional) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-5")
LLM_MAX_TOKENS = 400
LLM_SYSTEM_PROMPT = (
    f"You are {ASSISTANT_NAME}, a helpful voice assistant. "
    "Keep answers short and conversational (1-3 sentences) since they "
    "will be read aloud."
)
