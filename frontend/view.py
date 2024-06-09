import tkinter as tk
from tkinter import ttk


class View(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vorlesungsassistent")
        self.configure(bg='#f0f0f0')

        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Segoe UI', 12))
        self.style.configure('TButton', font=('Segoe UI', 12))
        self.style.configure('TEntry', font=('Segoe UI', 12))

        self.link_label = ttk.Label(self, text="Vorlesung Link:")
        self.link_label.grid(row=0, column=0, padx=10, pady=10)

        self.link_entry = ttk.Entry(self, width=50)
        self.link_entry.grid(row=0, column=1, padx=10, pady=10)

        self.link_button = ttk.Button(self, text="Analysieren")
        self.link_button.grid(row=0, column=2, padx=10, pady=10)

        self.chat_label = ttk.Label(self, text="Chat Eingabe:")
        self.chat_label.grid(row=1, column=0, padx=10, pady=10)

        self.chat_entry = ttk.Entry(self, width=50)
        self.chat_entry.grid(row=1, column=1, padx=10, pady=10)

        self.chat_button = ttk.Button(self, text="Senden")
        self.chat_button.grid(row=1, column=2, padx=10, pady=10)

        self.chat_output = tk.Text(self, width=80, height=20)
        self.chat_output.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def display_message(self, message):
        self.chat_output.insert(tk.END, message + "\n")
        self.chat_output.see(tk.END)
