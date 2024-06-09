import threading
from tkinter import messagebox
from frontend.model import Model
from frontend.view import View


class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.link_button.config(command=self.download_and_transcribe)
        self.view.chat_button.config(command=self.send_chat)

    def download_and_transcribe(self):
        url = self.view.link_entry.get()
        if not url:
            messagebox.showerror("Eingabe Fehler", "Bitte gib einen gültigen Link an.")
            return

        threading.Thread(target=self._download_and_transcribe_thread, args=(url,)).start()

    def _download_and_transcribe_thread(self, url):
        try:
            audio_path = self.model.download(url)
            transcript_path = self.model.transcribe(audio_path)
            self.model.load(transcript_path)
            messagebox.showinfo("Erfolgreich", "Transkript angefertigt. Chatbot bereit.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def send_chat(self):
        prompt = self.view.chat_entry.get()
        if not prompt:
            messagebox.showerror("Input Error", "Please enter a message to send.")
            return

        self.view.chat_button.config(state='disabled')
        threading.Thread(target=self._send_chat_thread, args=(prompt,)).start()

    def _send_chat_thread(self, prompt):
        try:
            response = self.model.chat(prompt)
            self.view.display_message("You: " + prompt)
            self.view.display_message("Bot: " + response)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.view.chat_button.config(state='normal')