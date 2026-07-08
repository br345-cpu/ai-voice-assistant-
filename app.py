import threading

from flask import Flask, render_template_string, request, jsonify
try:
    # When running as `python -m voice_assistant.app`
    from voice_assistant.assistant import Assistant
except ModuleNotFoundError:
    # When running as `python voice_assistant/app.py`
    from assistant import Assistant



try:
    import psutil  # optional dependency for server telemetry
except ImportError:  # pragma: no cover
    psutil = None

import time



app = Flask(__name__)

# IMPORTANT: avoid initializing audio devices (SpeechInput/SpeechOutput)
# at import time. Web UI should be able to start even if microphone/TTS
# dependencies are missing or fail.
_assistant = None

def get_assistant() -> Assistant:
    global _assistant
    if _assistant is None:
        _assistant = Assistant()
    return _assistant



HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
<title>JARVIS HUD</title>
  <style>
    :root {
      --bg1: #060816;
      --bg2: #111827;
      --panel: rgba(10, 18, 34, 0.72);
      --border: rgba(255,255,255,0.14);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #6ee7ff;
      --accent2: #8b5cf6;
    }
    * { box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      margin: 0;
      min-height: 100vh;
      color: var(--text);
background:
      radial-gradient(circle at top left, rgba(251,191,36,0.20), transparent 32%),
                  radial-gradient(circle at bottom right, rgba(239,68,68,0.22), transparent 38%),
                  radial-gradient(circle at 60% 40%, rgba(99,102,241,0.12), transparent 45%),
                  linear-gradient(135deg, #05070f, #101a33);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      overflow: hidden;
      position: relative;
    }
    body::before {
      content: '';
      position: absolute;
      inset: 0;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'%3E%3Crect width='600' height='600' rx='40' fill='%23ffffff' fill-opacity='0.04'/%3E%3Ccircle cx='180' cy='210' r='72' fill='%23fbbf24' fill-opacity='0.9'/%3E%3Ccircle cx='180' cy='210' r='46' fill='%23fef3c7'/%3E%3Ccircle cx='158' cy='195' r='8' fill='%23000'/%3E%3Ccircle cx='202' cy='195' r='8' fill='%23000'/%3E%3Cpath d='M146 246c16 22 46 24 66 0' stroke='%23000' stroke-width='7' fill='none' stroke-linecap='round'/%3E%3Crect x='112' y='320' width='136' height='110' rx='30' fill='%230f172a'/%3E%3Crect x='132' y='336' width='96' height='60' rx='16' fill='%23e2e8f0'/%3E%3Crect x='320' y='120' width='172' height='132' rx='28' fill='%236ee7ff' fill-opacity='0.85'/%3E%3Ccircle cx='413' cy='185' r='46' fill='%23f8fafc'/%3E%3Ccircle cx='394' cy='178' r='7' fill='%23000'/%3E%3Ccircle cx='432' cy='178' r='7' fill='%23000'/%3E%3Cpath d='M385 205c14 14 36 14 50 0' stroke='%23000' stroke-width='6' fill='none' stroke-linecap='round'/%3E%3Cpath d='M337 265c28 40 92 40 120 0' stroke='%230f172a' stroke-width='12' fill='none' stroke-linecap='round'/%3E%3Cpath d='M360 405c40 26 102 24 142 0' stroke='%238b5cf6' stroke-width='12' fill='none' stroke-linecap='round'/%3E%3C/svg%3E") center/cover no-repeat;
      opacity: 0.24;
      pointer-events: none;
      transform: rotate(-8deg) scale(1.08);
      filter: blur(0.4px);
    }
    .container {
      width: 100%;
      max-width: 820px;
      padding: 24px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.35);
      backdrop-filter: blur(18px);
      position: relative;
      z-index: 1;
    }
    .avatar {
      position: absolute;
      top: -38px;
      right: -28px;
      width: 96px;
      height: 96px;
      border-radius: 50%;
      background: linear-gradient(135deg, #fde68a, #fb923c);
      border: 4px solid rgba(255,255,255,0.2);
      box-shadow: 0 12px 28px rgba(0,0,0,0.25);
      display: grid;
      place-items: center;
      font-size: 42px;
      animation: bob 3s ease-in-out infinite;
      z-index: 2;
    }
    .orb {
      position: absolute;
      bottom: -24px;
      left: -24px;
      width: 84px;
      height: 84px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #ffffff, var(--accent), var(--accent2));
      box-shadow: 0 0 30px rgba(110,231,255,0.4);
      animation: pulseOrb 2.8s ease-in-out infinite;
      z-index: 0;
    }
    .spark {
      position: absolute;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 0 10px #fff;
      animation: spark 1.8s infinite ease-out;
      opacity: 0;
    }
    .spark.one { bottom: 8px; left: 10px; animation-delay: 0.2s; }
    .spark.two { bottom: 32px; left: 4px; animation-delay: 0.7s; }
    .spark.three { bottom: 18px; left: 36px; animation-delay: 1.1s; }
    @keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    @keyframes pulseOrb { 0%,100% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.08); opacity: 1; } }
    @keyframes spark { 0% { transform: translateY(0) scale(0.6); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(-22px) scale(1.3); opacity: 0; } }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--accent);
    }
    .dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(90deg, var(--accent), var(--accent2)); box-shadow: 0 0 14px var(--accent); }
    .subtitle { color: var(--muted); margin-top: 6px; font-size: 15px; }
    .chat {
      margin-top: 16px;
      padding: 14px;
      background: rgba(255,255,255,0.04);
      border-radius: 16px;
      min-height: 320px;
      max-height: 440px;
      overflow-y: auto;
      border: 1px solid rgba(255,255,255,0.08);
    }
    .message { margin: 10px 0; padding: 12px 14px; border-radius: 14px; line-height: 1.5; font-size: 15px; }
    .user { background: linear-gradient(90deg, rgba(110,231,255,0.22), rgba(59,130,246,0.2)); margin-left: 40px; }
    .assistant { background: rgba(255,255,255,0.08); margin-right: 40px; }
    .typing { display: inline-flex; gap: 4px; align-items: center; padding: 10px 12px; }
    .typing span { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); animation: pulse 1.2s infinite ease-in-out; }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes pulse { 0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }
    .input-row { display: flex; gap: 10px; margin-top: 14px; }
    .status-pill {
      margin-top: 10px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(255,255,255,0.06);
      color: var(--muted);
      font-size: 13px;
      border: 1px solid rgba(255,255,255,0.08);
      opacity: 0;
      transition: opacity 0.2s ease;
    }
    .status-pill.active {
      opacity: 1;
      color: #fef2f2;
      background: rgba(248, 113, 113, 0.16);
      border-color: rgba(248, 113, 113, 0.35);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #f87171;
      box-shadow: 0 0 10px #f87171;
      animation: blink 1s infinite;
    }
    @keyframes blink { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
    input[type=text] {
      flex: 1;
      padding: 13px 16px;
      font-size: 16px;
      border: 1px solid rgba(255,255,255,0.16);
      border-radius: 999px;
      background: rgba(255,255,255,0.06);
      color: white;
      outline: none;
    }
    input[type=text]::placeholder { color: #7c8ca8; }
    .icon-btn {
      padding: 12px 14px;
      font-size: 16px;
      border: none;
      border-radius: 999px;
      background: rgba(255,255,255,0.08);
      color: white;
      cursor: pointer;
    }
    .icon-btn.active { background: linear-gradient(90deg, var(--accent), var(--accent2)); color: #020617; }
    .send-btn {
      padding: 12px 18px;
      font-size: 16px;
      border: none;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), var(--accent2));
      color: #020617;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 0 18px rgba(110,231,255,0.24);
    }
    .send-btn:hover, .icon-btn:hover { transform: translateY(-1px); }
  </style>
</head>
<body>
  <div class="container">
    <div class="avatar">🤖</div>
    <div class="orb">
      <span class="spark one"></span>
      <span class="spark two"></span>
      <span class="spark three"></span>
    </div>
    <div class="header">
      <div>
Jarvis AI Voice Assistant
        <p class="subtitle">An advanced AI companion for conversations and commands.</p>
      </div>
      <div class="brand"><span class="dot"></span> LIVE</div>
    </div>
    <div id="chat" class="chat"><div class="message assistant">Assistant: Hello! I am ready.</div></div>
    <div class="input-row">
      <input id="message" type="text" placeholder="Ask something..." />
      <button class="icon-btn" id="micBtn" onclick="toggleListening()" title="Use microphone">🎤</button>
      <button class="send-btn" onclick="sendMessage()">Send</button>
    </div>
    <div id="statusPill" class="status-pill"><span class="status-dot"></span> Listening...</div>
  </div>
  <script>
    const input = document.getElementById('message');
    const chat = document.getElementById('chat');
    const micBtn = document.getElementById('micBtn');
    const statusPill = document.getElementById('statusPill');
    let recognition;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.interimResults = false;
      recognition.continuous = false;

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        input.value = transcript;
        micBtn.classList.remove('active');
        statusPill.classList.remove('active');
        sendMessage();
      };

      recognition.onerror = () => {
        micBtn.classList.remove('active');
        statusPill.classList.remove('active');
      };

      recognition.onend = () => {
        micBtn.classList.remove('active');
        statusPill.classList.remove('active');
      };
    }

    function toggleListening() {
      if (!recognition) {
        alert('Speech recognition is not supported in this browser.');
        return;
      }
      if (micBtn.classList.contains('active')) {
        recognition.stop();
        return;
      }
      micBtn.classList.add('active');
      statusPill.classList.add('active');
      recognition.start();
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;
      const userMessage = document.createElement('div');
      userMessage.className = 'message user';
      userMessage.textContent = `You: ${text}`;
      chat.appendChild(userMessage);
      input.value = '';
      chat.scrollTop = chat.scrollHeight;
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
      });
      const data = await response.json();
      const typing = document.createElement('div');
      typing.className = 'message assistant typing';
      typing.innerHTML = '<span></span><span></span><span></span>';
      chat.appendChild(typing);
      chat.scrollTop = chat.scrollHeight;

      setTimeout(() => {
        typing.remove();
        const assistantMessage = document.createElement('div');
        assistantMessage.className = 'message assistant';
        assistantMessage.textContent = `Assistant: ${data.reply}`;
        chat.appendChild(assistantMessage);
        chat.scrollTop = chat.scrollHeight;
      }, 650);
    }

    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        sendMessage();
      }
    });
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    text = data.get("message", "")

    # Avoid blocking the Flask request thread for long TTS/LLM work.
    # Flask will wait for this, but TTS/LLM happens without tying up
    # other server activity.
    reply_holder = {"reply": ""}

    def _work():
        reply_holder["reply"] = get_assistant().respond(text)


    t = threading.Thread(target=_work, daemon=True)
    t.start()
    t.join(timeout=20)

    if not reply_holder["reply"]:
        # If the assistant is still working, respond so the page doesn't
        # error; client can re-try.
        return jsonify({"reply": "I'm still working on that..."})

    return jsonify({"reply": reply_holder["reply"]})




@app.route("/status")
def status():
    # psutil is server-side telemetry; browser handles battery-like features.
    if psutil is None:
        return jsonify(
            {
                "cpu_usage": "N/A",
                "ram_usage": "N/A",
                "network_speed": "N/A",
                "battery_status": "N/A",
                "gpu_usage": "N/A",
            }
        )

    try:
        cpu = psutil.cpu_percent(interval=0.2)

        vm = psutil.virtual_memory()
        ram = vm.percent
        net = psutil.net_io_counters()
        return jsonify(
            {
                "cpu_usage": round(cpu, 1),
                "ram_usage": round(ram, 1),
                "network_speed": "N/A",
                "battery_status": "N/A",
                "gpu_usage": "N/A",
                "net_io": {
                    "bytes_sent": int(net.bytes_sent),
                    "bytes_recv": int(net.bytes_recv),
                },
            }
        )
    except Exception:
        return jsonify(
            {
                "cpu_usage": "N/A",
                "ram_usage": "N/A",
                "network_speed": "N/A",
                "battery_status": "N/A",
                "gpu_usage": "N/A",
            }
        )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

