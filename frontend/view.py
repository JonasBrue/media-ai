import tkinter as tk
from tkinter import ttk, filedialog


class View(tk.Tk):
    """
    The View class handles the user interface and provides elements for user interaction.
    """
    def __init__(self):
        super().__init__()
        self.title("Vorlesungsassistent")
        self.geometry("800x600")
        self.configure(bg='#f0f0f0')

        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Segoe UI', 12))
        self.style.configure('TButton', font=('Segoe UI', 12))
        self.style.configure('TEntry', font=('Segoe UI', 12))

        self.button_state = 'normal'

        # Video
        self.input_video_label = tk.Label(self, text="Vorlesung:")
        self.input_video_label.grid(row=0, column=0, padx=10, pady=10)

        self.input_video_entry = tk.Entry(self, width=50)
        self.input_video_entry.grid(row=0, column=1, padx=10, pady=10)

        self.select_video_button = tk.Button(self, text="Datei auswählen", command=self.select_video)
        self.select_video_button.grid(row=0, column=2, padx=10, pady=10)

        self.analyse_video_button = tk.Button(self, text="Analysieren")
        self.analyse_video_button.grid(row=0, column=3, padx=10, pady=10)

        # Chat Window
        self.chat_window_text = tk.Text(self, state='disabled', height=20, width=80)
        self.chat_window_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Chat Input
        self.send_message_entry = tk.Entry(self, width=70)
        self.send_message_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.send_message_button = tk.Button(self, text="Senden")
        self.send_message_button.grid(row=2, column=2, padx=10, pady=10)

        # Settings
        self.use_transcript_var = tk.BooleanVar()
        self.use_transcript_check = tk.Checkbutton(self, text="Transkript an Chatbot senden", variable=self.use_transcript_var)
        self.use_transcript_check.grid(row=3, column=0, padx=10, pady=10)

        self.use_video_var = tk.BooleanVar()
        self.use_video_check = tk.Checkbutton(self, text="Videoabschnitte an Chatbot senden", variable=self.use_video_var)
        self.use_video_check.grid(row=3, column=1, padx=10, pady=10)

        self.clear_chat_button = tk.Button(self, text="Chat leeren")
        self.clear_chat_button.grid(row=3, column=2, padx=10, pady=10)

    def select_video(self):
        """
        Opens a file dialog to select a video file and displays its path in the entry.
        """
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Video", "*.mp4")])
        if file_path:
            self.input_video_entry.delete(0, tk.END)
            self.input_video_entry.insert(0, file_path)

    def display_message(self, text):
        """
        Displays a message in the chat window.
        """
        self.chat_window_text.config(state='normal')
        self.chat_window_text.insert(tk.END, text + "\n")
        self.chat_window_text.config(state='disabled')

    def delete_messages(self):
        """
        Clears all messages from the chat window.
        """
        self.chat_window_text.config(state='normal')
        self.chat_window_text.delete(1.0, 'end')
        self.chat_window_text.config(state='disabled')

    def toggle_button_state(self):
        """
        Toggles button states during processing to prevent simultaneous actions and spamming.
        """
        if self.button_state == 'normal':
            self.button_state = 'disabled'
            self.analyse_video_button.config(state='disabled')
            self.send_message_button.config(state='disabled')
            self.clear_chat_button.config(state='disabled')
        else:
            self.button_state = 'normal'
            self.analyse_video_button.config(state='normal')
            self.send_message_button.config(state='normal')
            self.clear_chat_button.config(state='normal')
