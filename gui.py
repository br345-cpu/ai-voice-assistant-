import tkinter as tk
from tkinter import scrolledtext

from voice_assistant.assistant import Assistant



class VoiceAssistantGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("700x450")

        self.assistant = Assistant()

        self.input_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Ask your assistant", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.output = scrolledtext.ScrolledText(frame, height=16, state="disabled")
        self.output.pack(fill="both", expand=True, pady=(8, 10))

        entry = tk.Entry(frame, textvariable=self.input_var, font=("Segoe UI", 11))
        entry.pack(fill="x", pady=(0, 8))
        entry.bind("<Return>", self.handle_submit)

        button = tk.Button(frame, text="Send", command=self.handle_submit)
        button.pack(anchor="e")

    def handle_submit(self, _event=None):
        import threading

        text = self.input_var.get().strip()
        if not text:
            return

        self.append_text(f"You: {text}")
        self.input_var.set("")

        # Compute the reply off the Tk main thread to prevent UI freezing.
        def _work():
            reply = self.assistant.respond(text)
            self.root.after(0, lambda: self.append_text(f"Assistant: {reply}"))

        threading.Thread(target=_work, daemon=True).start()


    def append_text(self, message: str):
        self.output.configure(state="normal")
        self.output.insert(tk.END, message + "\n")
        self.output.configure(state="disabled")
        self.output.yview(tk.END)


def launch_gui():
    root = tk.Tk()
    VoiceAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
