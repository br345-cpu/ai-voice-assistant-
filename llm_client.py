"""
Optional LLM fallback: when a rule-based command doesn't match what the
user said, forward it to Claude for a real answer. Fully optional -
if ANTHROPIC_API_KEY isn't set, the assistant just admits it doesn't know.
"""

from voice_assistant import config


_client = None
_history = []
MAX_HISTORY_TURNS = 6  # keep the last N exchanges for context


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic
        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def is_available() -> bool:
    return bool(config.ANTHROPIC_API_KEY)


def ask(user_text: str) -> str:
    """Send user_text to Claude with recent conversation history and
    return a short spoken-style reply.

    If Anthropic isn't configured, fall back to a neutral response that
    doesn't tell the user how to configure env vars (keeps UX clean).
    """
    if not is_available():
        return "I can’t answer that right now. Try asking a built-in command."


    global _history
    client = _get_client()

    _history.append({"role": "user", "content": user_text})
    _history = _history[-(MAX_HISTORY_TURNS * 2):]

    try:
        response = client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=config.LLM_MAX_TOKENS,
            system=config.LLM_SYSTEM_PROMPT,
            messages=_history,
        )
        reply = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        _history.append({"role": "assistant", "content": reply})
        return reply or "I'm not sure how to answer that."
    except Exception as e:
        return f"I had trouble reaching the language model: {e}"
