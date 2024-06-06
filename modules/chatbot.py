from gpt4all import GPT4All
import json
import os
import logging


class ChatBot:

    def __init__(self):
        logging.info("Module: Chatbot starting...")
        model = "em_german_mistral_v01.Q4_0.gguf"
        self.chatbot = GPT4All(model_name=model)
        logging.info("Module: Chatbot initialized.")

    def summarize(self, path_to_transcript):
        """
        Summarize the transcript file.

        Returns:
        str: The path to the summary  file.
        """
        path_to_chat = path_to_transcript.replace("-transcript.json", "-chat.json")
        if os.path.exists(path_to_chat):
            logging.info("Chat-File already exists at: " + path_to_chat)
            return path_to_chat

        # Read the transcript file
        with open(path_to_transcript, 'r', encoding='utf-8') as file:
            transcript_text = json.load(file)

        try:
            logging.info("Starting to summarize, please wait...")
            cmd = "Ich habe eine Frage zum folgendem Transkript eines Videos. Hier ist das Transkript: " + transcript_text["text"] + "Transkript Ende. Von welchem Kanal kommt dieses Video?"
            with self.chatbot.chat_session():
                response1 = self.chatbot.generate(prompt=cmd)
                print(self.chatbot.current_chat_session)
            logging.info("Summary created.")

            with open(path_to_chat, 'w', encoding='utf-8') as file:
                json.dump(response1, file, ensure_ascii=False, indent=4)
            logging.info("Saved to txt file at: " + path_to_chat)
            return path_to_chat
        except:
            logging.error("Summary failed.")
            raise