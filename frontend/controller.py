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
        if not url or url == "Youtube-Link oder Dateipfad eingeben...":
            messagebox.showerror("Eingabe Fehler", "Bitte gib einen gültigen Link an.")
            return
        self.view.toggle_button_state()
        backend_id = self.view.use_backend_to_transcribe.get()
        threading.Thread(target=self._process_video_thread,
                         args=(backend_id, url)).start()

    def _process_video_thread(self, backend_id, url):
        """
        Processes the video in a separate thread, to avoid blocking the UI.
        """
        try:
            self.model.transcribe(backend_id, url)
            self.view.check_transcript_checkbox()
            messagebox.showinfo("Erfolgreich", "Transkript angefertigt. Chatbot bereit.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
        finally:
            costs = self.model.calculate_costs()
            self.view.display_api_usage_costs(costs)
            self.view.toggle_button_state()

    def send_message(self):
        """
        Sends a message to the chatbot, validating input and starting a new thread.
        """
        user_input = self.view.send_message_entry.get()
        if not user_input or user_input == "Nachricht eingeben...":
            messagebox.showerror("Eingabe Fehler", "Bitte schreibe eine Nachricht.")
            return
        backend_id = self.view.use_backend_to_chat.get()
        use_transcript = self.view.use_transcript_var.get()
        use_video = self.view.use_video_var.get()
        self.view.toggle_button_state()
        self.view.display_message("Du: " + user_input)
        self.view.clear_input_field()
        threading.Thread(target=self._process_message_thread,
                         args=(backend_id, user_input, use_transcript, use_video)).start()

    def _process_message_thread(self, backend_id, user_input, use_transcript, use_video):
        """
        Processes the chatbot message in a separate thread, to keep the UI responsive.
        """
        try:
            response = self.model.chat(backend_id, user_input, use_transcript, use_video)
            self.view.display_message("Bot: " + response)
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            self.view.display_message("Bot: Fehler, versuchs nochmal.")
        finally:
            costs = self.model.calculate_costs()
            self.view.display_api_usage_costs(costs)
            self.view.toggle_button_state()

    def clear_chat(self):
        self.view.toggle_button_state()
        threading.Thread(target=self.model.clear_chat, args=()).start()
        self.view.clear_chat()
        self.view.toggle_button_state()
