from gpt4all import GPT4All
import json
import logging


class ChatBot:

    def __init__(self, path_to_transcript):
        logging.info("Starting ...")

        model = "em_german_mistral_v01.Q4_0.gguf"
        self.chatbot = GPT4All(model_name=model)
        self.session = self.chatbot.chat_session()

        with open(path_to_transcript, 'r', encoding='utf-8') as file:
            transcript = json.load(file)
        self.transcript_text = transcript["text"]
        self.transcript_segments = transcript["segments"]

        logging.info("Started.")

    def chat(self, prompt):
        print(prompt)
        with self.session:
            prompt = f"Vorlesung Transkript: {self.transcript_text}\n\nStudent Frage: {prompt}\nDeine Antwort: "
            response = self.chatbot.generate(prompt=prompt)
            print(response)
            logging.info("Replied to user's input.")
            return response

    def reset(self):
        self.session = self.chatbot.chat_session()
        logging.info("Chat session cleared.")
