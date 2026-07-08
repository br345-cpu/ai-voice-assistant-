# AI Voice Assistant (Python)

A push-to-talk voice assistant: press Enter, speak, and it transcribes
your speech, tries to match a built-in command, and falls back to
Claude for anything else (optional).

## Features

- 🎙️ Speech-to-text via microphone (push-to-talk, no wake-word false triggers)
- 🔊 Offline text-to-speech (works without internet)
- 🧠 Built-in commands: time, date, jokes, "who are you", open websites,
  Wikipedia lookups
- 🤖 Optional smart fallback: anything not matched by a command gets sent
  to Claude for a real conversational answer
- 🧩 Easy to extend — add a new command in `commands.py` in a few lines

## Project structure

```
voice_assistant/
├── main.py            # entry point — run this
├── assistant.py        # main loop tying everything together
├── config.py           # all settings, via environment variables
├── speech_input.py      # microphone -> text (SpeechRecognition)
├── speech_output.py     # text -> speech (pyttsx3, offline)
├── commands.py          # rule-based command handlers
├── llm_client.py        # optional Claude fallback for open questions
├── list_voices.py        # utility: list available TTS voices
└── requirements.txt
```

## Setup

### 1. Quick start on Windows

From the project folder, run:

```powershell
setup.bat
run.bat
```

This creates a virtual environment, installs dependencies, and starts the assistant.

### 2. Install system audio dependencies

PyAudio needs the PortAudio library installed first.

**macOS:**
```bash
brew install portaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio espeak
```
(`espeak` is the offline TTS voice engine used by pyttsx3 on Linux.)

**Windows:**
No extra system install needed — the PyAudio wheel bundles PortAudio.

### 3. Install Python dependencies

```bash
cd voice_assistant
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If `pip install pyaudio` fails on Windows, install the prebuilt wheel instead:
```bash
pip install pipwin
pipwin install pyaudio
```

### 4. (Optional) enable smart LLM answers

By default, anything the assistant doesn't recognize as a command gets
a "I don't know that" reply. To have it answer real questions via Claude:

```bash
export ANTHROPIC_API_KEY="your-key-here"   # Windows: set ANTHROPIC_API_KEY=...
```

Get a key at https://console.anthropic.com. Without this set, everything
else in the assistant still works fine — you just lose open-ended Q&A.

### 5. Run it

```bash
python main.py
```

Press Enter, speak your request, and wait for the reply. Say "quit",
"exit", "stop", or "goodbye" to end the session.

## Built-in commands (say things like...)

| You say | It does |
|---|---|
| "What time is it?" | Tells the current time |
| "What's today's date?" | Tells the current date |
| "Tell me a joke" | Tells a joke |
| "Who are you?" | Introduces itself |
| "Open YouTube" / "Open Google" / "Open Gmail" / "Open Wikipedia" / "Open GitHub" | Opens the site in your browser |
| "Who is Ada Lovelace?" / "What is quantum computing?" | Looks up a short Wikipedia summary |
| "Quit" / "exit" / "goodbye" | Ends the session |
| Anything else | Forwarded to Claude (if API key set), otherwise a fallback message |

## Customizing

**Change the assistant's name:**
```bash
export ASSISTANT_NAME="Nova"
```

**Change speech rate/volume:** edit `TTS_RATE` / `TTS_VOLUME` in `config.py`
or set them as environment variables.

**Change TTS voice:** run `python list_voices.py` to see options, then set
`TTS_VOICE_ID` to the id you want.

**Add a new command:** open `commands.py`, write a function like:

```python
def handle_weather(text: str):
    if "weather" in text:
        return "It's sunny and 75 degrees."  # wire up a real API here
    return None
```

then add `handle_weather` to the `HANDLERS` list at the bottom of the file.

## Going fully offline

Two parts of this project use the internet by default:
- Speech recognition uses Google's free web API (`recognize_google`)
- Wikipedia lookups and the LLM fallback obviously need internet

To go fully offline, swap speech recognition to CMU PocketSphinx:

```bash
pip install pocketsphinx
```

Then in `speech_input.py`, replace:
```python
text = self.recognizer.recognize_google(audio, language=config.STT_LANGUAGE)
```
with:
```python
text = self.recognizer.recognize_sphinx(audio)
```

Sphinx is less accurate than Google's API but works with zero internet
connection, which is handy for embedded/offline setups.

## Troubleshooting

- **"No module named 'pyaudio'"** → see the system dependency step above,
  your OS needs PortAudio installed before `pip install pyaudio` works.
- **Microphone not detected** → run this to list input devices and confirm
  your mic shows up:
  ```python
  import speech_recognition as sr
  print(sr.Microphone.list_microphone_names())
  ```
- **No sound on Linux** → make sure `espeak` is installed (see step 1).
- **Recognition is slow/inaccurate** → try speaking closer to the mic and
  in a quieter room; `recognizer.adjust_for_ambient_noise` runs automatically
  on startup but a very noisy environment can still trip it up.
