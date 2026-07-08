#!/usr/bin/env python3
"""Entry point for the AI voice assistant."""

import argparse

from voice_assistant.assistant import Assistant
from voice_assistant.gui import launch_gui



def launch_web_ui() -> None:
    from voice_assistant.app import app


    app.run(debug=True, host="0.0.0.0", port=5000)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the voice assistant")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="launch the graphical interface instead of the terminal loop",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="launch the web interface in the browser",
    )
    args, _ = parser.parse_known_args()

    if args.gui:
        launch_gui()
        return

    if getattr(args, "web", False):
        launch_web_ui()
        return

    try:
        Assistant().run()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
