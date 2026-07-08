"""
Speech-to-text input.

Uses push-to-talk: you press Enter, speak, and the assistant transcribes
what you said. This avoids the false-activation issues of wake-word or
always-on listening, and needs no extra wake-word engine/model.

Recognition is done via SpeechRecognition's Google Web Speech API
(free, no API key, but requires an internet connection). If you want a
fully offline setup instead, see the README for swapping in
`recognize_sphinx` (CMU PocketSphinx).
"""

from voice_assistant import config


try:
    import speech_recognition as sr
except ImportError:
    sr = None


class SpeechInput:
    def __init__(self):
        self.available = sr is not None
        self._error_message = (
            "Speech recognition is unavailable in this environment. "
            "Install the audio dependencies and use a compatible Python runtime."
        )
        self.recognizer = None
        self.microphone = None

        if not self.available:
            return

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Calibrate once for ambient noise so short utterances aren't cut off.
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)

    def listen_once(self) -> str | None:
        """
        Wait for the user to press Enter, then record and transcribe
        one utterance. Returns the recognized text, or None if nothing
        could be understood.
        """
        if not self.available:
            print(self._error_message)
            return None

        input("\n[Press Enter, then speak]")

        with self.microphone as source:
            print("Listening...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=config.STT_TIMEOUT,
                    phrase_time_limit=config.STT_PHRASE_TIME_LIMIT,
                )
            except sr.WaitTimeoutError:
                print("(didn't hear anything)")
                return None

        print("Transcribing...")
        try:
            text = self.recognizer.recognize_google(
                audio, language=config.STT_LANGUAGE
            )
            print(f"You: {text}")
            return text
        except sr.UnknownValueError:
            print("(couldn't understand that)")
            return None
        except sr.RequestError as e:
            print(f"(speech recognition service error: {e})")
            return None
