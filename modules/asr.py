import torch
import whisper
import json
import os
import logging


class AutomaticSpeechRecognition:

    def __init__(self, path_to_audio):
        """
        Initializes the AutomaticSpeechRecognition instance with all paths set.

        Parameters:
        path_to_audio (str): The path to the audio file.
        """
        if torch.cuda.is_available():
            self.device = "cuda"
            logging.info("CUDA device is available. Using GPU.")
        else:
            self.device = "cpu"
            logging.info("CUDA device not available. Using CPU.")
        self.model = "base"  # available: tiny, base, small, medium or large
        self.path_to_storage = "./storage/"
        self.path_to_audio = path_to_audio
        self.path_to_transcript = path_to_audio.replace("-audio.mp3", "-transcript.json")
        logging.info("Module: AutomaticSpeechRecognition initialized.")

    def transcribe(self):
        """
        Transcribes the audio file if it doesn't already exist.

        Returns:
        str: The path to the transcript file.
        """
        if os.path.exists(self.path_to_transcript):
            logging.info("Transcript-File already exists at: " + self.path_to_transcript)
            return self.path_to_transcript

        try:
            logging.info("Starting to transcribe, please wait...")
            model = whisper.load_model(self.model, device=self.device)
            result = model.transcribe(self.path_to_audio, fp16=False)
            logging.info("Transcription successful.")

            with open(self.path_to_transcript, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            logging.info("Saved to txt file at: " + self.path_to_transcript)
            return self.path_to_transcript
        except:
            logging.error("Transcription failed.")
            raise