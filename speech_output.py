"""
Text-to-speech output. Uses pyttsx3, which works fully offline and
runs on Windows (SAPI5), macOS (NSSpeechSynthesizer), and Linux (espeak).
"""

import threading

from voice_assistant import config


try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class SpeechOutput:
    def __init__(self):
        self.engine = None
        self._error_message = (
            "Text-to-speech is unavailable in this environment. "
            "Install pyttsx3 and a compatible speech engine."
        )
        self._lock = threading.Lock()

        if pyttsx3 is None:
            return

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", config.TTS_RATE)
        self.engine.setProperty("volume", config.TTS_VOLUME)

        if config.TTS_VOICE_ID:
            self.engine.setProperty("voice", config.TTS_VOICE_ID)

    def say(self, text: str):
        """Speak text out loud without blocking the caller.

        pyttsx3's `runAndWait()` is blocking; this method runs it in a
        background thread so GUI/web callers stay responsive.
        """
        print(f"{config.ASSISTANT_NAME}: {text}")
        if self.engine is None:
            print(self._error_message)
            return

        def _worker():
            with self._lock:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except RuntimeError:
                    # Engine can be re-entered while busy.
                    print("Speech output skipped because the engine was busy.")

        threading.Thread(target=_worker, daemon=True).start()

