import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedTk


class View(ThemedTk):
    """
    The View class handles the user interface and provides elements for user interaction.
    """

    def __init__(self):
        super().__init__(theme="yaru")
        self.title("Vorlesungsassistent")
        self.geometry('800x800')
        self.minsize(800, 800)
        self.configure(bg='#f0f0f0')
        self.button_state = 'normal'
        self.font = ('Segoe UI', 12)

        self.style = ttk.Style()
        self.style.configure('.', font=self.font)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Video
        self.input_frame = ttk.Frame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        self.input_video_label = ttk.Label(self.input_frame, text="1. Vorlesung wählen:")
        self.input_video_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.input_video_entry = ttk.Entry(self.input_frame, font=self.font)
        self.input_video_entry.grid(row=0, column=1, columnspan=2, padx=(10,1), pady=10, sticky="ew")
        self.set_placeholder_text(self.input_video_entry, "Youtube-Link oder Dateipfad eingeben...")

        self.select_video_button = ttk.Button(self.input_frame, text="Dateipfad auswählen", command=self.select_video)
        self.select_video_button.grid(row=0, column=3, padx=(1,10), pady=10, sticky="ew")

        self.computation_selection_label = ttk.Label(self.input_frame, text="2. Transkript generieren:")
        self.computation_selection_label.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.use_api_to_transcribe = tk.BooleanVar(value=False)
        self.local_computation_radiobutton = ttk.Radiobutton(self.input_frame, text="Deine Hardware nutzen",
                                                             variable=self.use_api_to_transcribe, value=False)
        self.local_computation_radiobutton.grid(row=1, column=1, padx=(10,1), pady=10, sticky="w")

        self.api_computation_radiobutton = ttk.Radiobutton(self.input_frame, text="OpenAI-Server verwenden",
                                                           variable=self.use_api_to_transcribe, value=True)
        self.api_computation_radiobutton.grid(row=1, column=2, padx=(1,1), pady=10, sticky="w")

        self.analyse_video_button = ttk.Button(self.input_frame, text="Starten")
        self.analyse_video_button.grid(row=1, column=3, padx=(1,10), pady=10, sticky="ew")




        # Chat Window
        self.window_frame = ttk.Frame(self)
        self.window_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="ns")
        self.window_frame.grid_rowconfigure(0, weight=1)
        self.window_frame.grid_columnconfigure(0, weight=1)

        self.chat_window_text = tk.Text(self.window_frame, width=85, state='disabled', wrap='word', font=self.font)
        self.chat_window_text.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ns")

        self.chat_scrollbar = ttk.Scrollbar(self.window_frame, orient=tk.VERTICAL, command=self.chat_window_text.yview)
        self.chat_scrollbar.grid(row=0, column=4, padx=5, pady=10, sticky='ns')
        self.chat_window_text['yscrollcommand'] = self.chat_scrollbar.set

        # Chat Input
        self.message_frame = ttk.Frame(self)
        self.message_frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

        self.send_message_entry = ttk.Entry(self.message_frame, width=62, font=self.font)
        self.send_message_entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        self.set_placeholder_text(self.send_message_entry, "Nachricht eingeben...")

        self.send_message_button = ttk.Button(self.message_frame, text="Senden")
        self.send_message_button.grid(row=0, column=4, padx=10, pady=10)
        self.send_message_entry.bind('<Return>', lambda event: self.send_message_button.invoke())

        self.use_transcript_var = tk.BooleanVar()
        self.use_transcript_check = ttk.Checkbutton(self.message_frame, text=" Transkript anhängen",
                                                    variable=self.use_transcript_var)
        self.use_transcript_check.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.use_video_var = tk.BooleanVar()
        self.use_video_check = ttk.Checkbutton(self.message_frame,
                                               text=" Videoabschnitte anhängen (Ressourcenintensiv)",
                                               variable=self.use_video_var)
        self.use_video_check.grid(row=1, column=2, columnspan=2, padx=10, pady=10)

        self.clear_chat_button = ttk.Button(self.message_frame, text="Chat leeren")
        self.clear_chat_button.grid(row=1, column=4, padx=10, pady=10)

        # Costs display
        self.costs_label = ttk.Label(self.message_frame, text="Kosten in dieser Sitzung: $0.00", font=self.font)
        self.costs_label.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

    def set_placeholder_text(self, entry, placeholder):
        """
        Sets a placeholder in the given entry widget.
        """

        def clear_placeholder(event):
            if event.widget.get() == placeholder:
                event.widget.delete(0, tk.END)
                event.widget.config(foreground='black')

        def add_placeholder(event):
            if event.widget.get() == '':
                event.widget.insert(0, placeholder)
                event.widget.config(foreground='grey')

        entry.insert(0, placeholder)
        entry.config(foreground='grey')
        entry.bind('<FocusIn>', clear_placeholder)
        entry.bind('<FocusOut>', add_placeholder)

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

    def clear_chat(self):
        """
        Clears all messages from the chat window.
        """
        self.chat_window_text.config(state='normal')
        self.chat_window_text.delete(1.0, 'end')
        self.chat_window_text.config(state='disabled')

    def clear_input_field(self):
        """
        Clears the input field in the chat input.
        """
        self.send_message_entry.delete(0, tk.END)

    def check_transcript_checkbox(self):
        """
        Sets the use_transcript_var to True and checks the checkbox.
        """
        self.use_transcript_var.set(True)

    def toggle_button_state(self):
        """
        Toggles button states during processing to prevent simultaneous actions and spamming.
        """
        self.button_state = 'disabled' if self.button_state == 'normal' else 'normal'
        call_api_buttons = [self.analyse_video_button, self.send_message_button, self.clear_chat_button]
        for button in call_api_buttons:
            button.config(state=self.button_state)

    def display_api_usage_costs(self, costs):
        """
        Displays the API usage costs in the costs label.
        """
        self.costs_label.config(text=f"Kosten in dieser Sitzung: ${costs:.2f}")
