from voice_assistant import commands
from voice_assistant import config
from voice_assistant import llm_client
from voice_assistant.speech_input import SpeechInput
from voice_assistant.speech_output import SpeechOutput



def _hud_format(user_text: str, main_reply: str) -> str:
    # Keep analysis short for speech + HUD readability.
    lowered = (user_text or "").lower().strip()
    if any(w in lowered for w in commands.EXIT_WORDS):
        analysis = "Exit command detected."
    else:
        analysis = "Command evaluation complete."

    # Lightweight metrics (deterministic to avoid test brittleness).
    confidence = 98 if commands.handle(user_text) is not None else 90
    complexity = "Low" if commands.handle(user_text) is not None else "Medium"

    # Address user as “Sir” per spec.
    if not main_reply:
        main_reply = "Sir, I don’t have a response yet."
    if "sir" not in main_reply.lower():
        main_reply = f"Sir, {main_reply}"

    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "◉ AI STATUS\n"
        "ONLINE\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🧠 ANALYSIS\n"
        f"{analysis}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚡ EXECUTION\n"
        f"{main_reply}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 SYSTEM METRICS\n"
        f"Confidence: {confidence}%\n"
        f"Complexity: {complexity}\n"
        "Estimated Time: Instant\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 RECOMMENDATIONS\n"
        "✓ If you want details, ask a follow-up.\n"
        "\n✓ COMPLETE"
    )


class Assistant:
    def __init__(self):
        self.ears = SpeechInput()
        self.mouth = SpeechOutput()

    def respond(self, text: str) -> str:
        reply = commands.handle(text)
        if reply is None:
            reply = llm_client.ask(text)

        self.mouth.say(reply)  # Speak the raw answer (more natural than HUD)

        # Preserve the original command response text for command-based UX.
        # Only wrap into HUD format for open-ended (LLM) replies.
        if reply is None:
            return _hud_format(text, "Sir, I don’t have a response yet.")

        # If a built-in command handled it, return plain reply (old commands UX).
        if commands.handle(text) is not None:
            return reply

        return _hud_format(text, reply)



    def run(self):
        self.mouth.say(
            f"{config.ASSISTANT_NAME} online. Press Enter and speak, "
            "or say 'quit' to exit."
        )
        while True:
            text = self.ears.listen_once()
            if text is None:
                continue

            self.respond(text)

            if any(w in text.lower() for w in commands.EXIT_WORDS):
                break


if __name__ == "__main__":
    Assistant().run()
