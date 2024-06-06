import torch
import whisper
import json
import os
import logging


class AutomaticSpeechRecognition:

    def __init__(self):
        logging.info("Starting ...")

        if torch.cuda.is_available():
            device = "cuda"
            logging.info("CUDA device is available. Using GPU.")
        else:
            device = "cpu"
            logging.info("CUDA device not available. Using CPU.")
        self.whisper = whisper.load_model(name="base", device=device)  # available: tiny, base, small, medium or large

        logging.info("Started.")

    def transcribe(self, path_to_audio):
        logging.info("Transcribing ...")
        path_to_transcript = path_to_audio.replace("-audio.mp3", "-transcript.json")
        if os.path.exists(path_to_transcript):
            logging.info("Transcript-File already exists at: " + path_to_transcript)
            return path_to_transcript

        try:
            result = self.whisper.transcribe(path_to_audio, fp16=False)
            logging.info("Transcription successful.")

            with open(path_to_transcript, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            logging.info("Saved to txt file at: " + path_to_transcript)

            return path_to_transcript
        except:
            logging.error("Transcription failed.")
            raise