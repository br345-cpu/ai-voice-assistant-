# TODO — JARVIS 3D Holographic AI Interface

## Step 1 — Implement HUD telemetry (real metrics)
- [ ] Add `psutil` dependency (server-side)
- [ ] Add `/status` endpoint in `voice_assistant/app.py` returning CPU/RAM/net/battery-like placeholders (battery is browser-only; server will provide what’s possible)
- [ ] Update top bar + right sidebar widgets to poll `/status`

## Step 2 — Upgrade center dashboard UI + animations
- [ ] Replace inline HTML/CSS in `voice_assistant/app.py` with multi-panel layout (top bar, left nav, center workspace, right widgets, bottom dock)
- [ ] Add scan lines + holographic energy pulses
- [ ] Ensure message enter animations: fade/slide/glow

## Step 3 — HUD response formatting
- [ ] Update `voice_assistant/assistant.py` to wrap every reply into the specified HUD template and address the user as “Sir”
- [ ] Ensure short “🧠 ANALYSIS” content and “📊 SYSTEM METRICS” fields

## Step 4 — Tests
- [ ] Update failing assertions in `voice_assistant/tests/*` (if reply text format changed)
- [ ] Run `pytest`

## Step 5 — Tkinter GUI (web-only unless requested)
- [ ] Verify Tkinter GUI still works; keep changes minimal (web-only priority)

