"""Run this to see which TTS voices are available on your machine,
then copy a voice id into config.py (TTS_VOICE_ID) or set it as the
TTS_VOICE_ID environment variable."""

import pyttsx3

engine = pyttsx3.init()
for voice in engine.getProperty("voices"):
    print(f"id: {voice.id}")
    print(f"  name:      {voice.name}")
    print(f"  languages: {voice.languages}")
    print(f"  gender:    {getattr(voice, 'gender', 'unknown')}")
    print()
