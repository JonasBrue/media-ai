from transformers import pipeline
import json
import os
import logging


class ChatBot:

    def __init__(self, path_to_transcript):
        """
        Initializes the ChatBot instance.

        Parameters:
        path_to_transcript (str): The path to the transcript file.
        """
        self.path_to_storage = "./storage/"
        self.path_to_transcript = path_to_transcript
        self.path_to_summary = path_to_transcript.replace("-transcript.json", "-summary.txt")
        logging.info("Module: Chatbot initialized.")

    def summarize(self):
        """
        Summarize the transcript file if it doesn't already exist.

        Returns:
        str: The path to the summary  file.
        """
        if os.path.exists(self.path_to_summary):
            logging.info("Summary-File already exists at: " + self.path_to_summary)
            return self.path_to_summary

        # Read the transcript file
        with open(self.path_to_transcript, 'r', encoding='utf-8') as file:
            transcript_text = json.load(file)

        try:
            logging.info("Starting to summerize, please wait...")
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            summary = summarizer(transcript_text['text'], max_length=150, min_length=30, do_sample=False)[0]['summary_text']
            logging.info("Summary created.")
            t = open(self.path_to_summary, "w")
            t.write(summary)
            t.close()
            logging.info("Saved to txt file at: " + self.path_to_summary)
            return self.path_to_summary
        except:
            logging.error("Summary failed.")
            raise