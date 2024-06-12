import threading
from tkinter import messagebox


class Controller:

    def __init__(self, view, model):
        """
        The Controller class handles user interactions and updates the View and Model accordingly.
        """
        self.view = view
        self.model = model
        # Set up UI button commands
        self.view.analyse_video_button.config(command=self.analyse_video)
        self.view.send_message_button.config(command=self.send_message)
        self.view.clear_chat_button.config(command=self.clear_chat)

    def analyse_video(self):
        """
        Starts the video analysis process, validating input and starting a new thread.
        """
        url = self.view.input_video_entry.get()
        if not url:
            messagebox.showerror("Eingabe Fehler", "Bitte gib einen gültigen Link an.")
            return
        self.view.toggle_button_state()
        threading.Thread(target=self._process_video_thread, args=(url,)).start()

    def _process_video_thread(self, url):
        """
        Processes the video in a separate thread, to avoid blocking the UI.
        """
        try:
            self.model.transcribe(url)
            messagebox.showinfo("Erfolgreich", "Transkript angefertigt. Chatbot bereit.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
        finally:
            self.view.toggle_button_state()

    def send_message(self):
        """
        Sends a message to the chatbot, validating input and starting a new thread.
        """
        prompt = self.view.send_message_entry.get()
        if not prompt:
            messagebox.showerror("Eingabe Fehler", "Bitte schreibe eine Nachricht.")
            return
        self.view.toggle_button_state()
        self.view.display_message("Du: " + prompt)
        use_transcript = self.view.use_transcript_var.get()
        use_video = self.view.use_video_var.get()
        threading.Thread(target=self._process_message_thread, args=(prompt, use_transcript, use_video)).start()

    def _process_message_thread(self, prompt, use_transcript, use_video):
        """
        Processes the chatbot message in a separate thread, to keep the UI responsive.
        """
        try:
            response = self.model.chat(prompt, use_transcript, use_video)
            self.view.display_message("Bot: " + response)
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            self.view.display_message("Bot: Fehler, versuchs nochmal.")
        finally:
            self.view.toggle_button_state()

    def clear_chat(self):
        self.view.toggle_button_state()
        threading.Thread(target=self.model.clear_chat, args=()).start()
        self.view.delete_messages()
        self.view.toggle_button_state()
