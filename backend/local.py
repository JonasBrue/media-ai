from gpt4all import GPT4All
import torch
import whisper
import json
import os
import logging
from backend.utils import convert_to_audio, convert_seconds_to_hms


class LOCAL:
    MODEL_CHATBOT = "em_german_mistral_v01.Q4_0.gguf"
    MODEL_TRANSCRIBER = "base"  # available: tiny, base, small, medium or large

    def __init__(self):
        """
        Loading transcriber and chatbot model.
        """
        if torch.cuda.is_available():
            device = "cuda"
            logging.info("CUDA device is available. Using GPU.")
        else:
            device = "cpu"
            logging.info("CUDA device not available. Using CPU.")
        self.whisper = whisper.load_model(name=self.MODEL_TRANSCRIBER, device=device)
        self.chatbot = GPT4All(model_name=self.MODEL_CHATBOT)
        self.chat_history = []
        self.costs = 0
        logging.info("Started.")

    def transcribe(self, video_input):
        """
        Transcribes the audio from a given video input.
        Converts video to audio and then transcribes the audio.
        Returns the path to the transcript JSON file.
        """
        logging.info("Transcribing ...")
        path_to_audio = convert_to_audio(video_input)
        path, _ = os.path.splitext(path_to_audio)
        path_to_transcript = path + ".json"

        if os.path.exists(path_to_transcript):
            logging.info("Operation done before. File already exists at: " + path_to_transcript)
        else:
            try:
                transcript_response = self.whisper.transcribe(path_to_audio)
                with open(path_to_transcript, 'w', encoding='utf-8') as file:
                    json.dump(transcript_response, file, ensure_ascii=False, indent=4)
                logging.info("Transcribing successful.")
            except Exception:
                raise Exception("Transcription failed. Try using the API instead")

        return path_to_transcript

    def chat(self, user_input, path_to_transcript, use_transcript, use_video):
        """
        Generates a chat response based on user input.
        Optionally including the transcript and video frames.
        """
        logging.info("Responding to user input ...")
        messages = "Sie sind ein hilfreicher Assistent, der Fragen von Studenten zu Vorlesungen beantwortet. " \
                   "Ihnen können Bilder und ein Transkript der Vorlesung zur Verfügung gestellt werden. " \
                   "Bitte geben Sie präzise und verständliche Antworten, die den Studenten helfen, " \
                   "die Inhalte der Vorlesung besser zu verstehen. "
        if self.chat_history:
            messages += "Dies war der bisherige Chatverlauf: ".join(self.chat_history)

        messages += self._add_content(path_to_transcript, use_transcript, use_video)

        if user_input:
            messages += f"{user_input}"

        response = self.chatbot.generate(prompt=messages)
        self.chat_history.append("Student: " + user_input)
        self.chat_history.append("Antwort: " + response)
        logging.info("Responding successful.")
        return response

    def clear_chat(self):
        self.chat_history = []
        logging.info("Chat history cleared.")

    def calculate_costs(self):
        return self.costs

    def _add_content(self, path_to_transcript, use_transcript, use_video):
        """
        Adds content to the user message based on the transcript and video frames if specified.
        """
        content = ""
        if use_transcript:
            if not os.path.exists(path_to_transcript):
                raise Exception("Transcript is not available.")
            with open(path_to_transcript, 'r', encoding='utf-8') as file:
                transcript = json.load(file)
            transcript_segments = transcript['segments']
            transcript_formatted = ""
            for segment in transcript_segments:
                start_time = convert_seconds_to_hms(segment['start'])
                end_time = convert_seconds_to_hms(segment['end'])
                text = segment['text']
                transcript_formatted += f"[{start_time} - {end_time}] {text}\n"
            content += f"Die Audiotranskription der Vorlesung ist: \n{transcript_formatted}"
        if use_video:
            raise Exception("Local Chatbot cannot process the video. Try using the API instead")
        return content
