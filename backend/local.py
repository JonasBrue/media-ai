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
            logging.info("CUDA-Gerät ist verfügbar. GPU wird verwendet.")
        else:
            device = "cpu"
            logging.info("CUDA-Gerät nicht verfügbar. CPU wird verwendet.")
        self.whisper = whisper.load_model(name=self.MODEL_TRANSCRIBER, device=device)
        self.chatbot = GPT4All(model_name=self.MODEL_CHATBOT)
        self.chat_history = []
        self.costs = 0
        logging.info("Gestartet.")

    def transcribe(self, video_input):
        """
        Transcribes the audio from a given video input.
        Converts video to audio and then transcribes the audio.
        Returns the path to the transcript JSON file.
        """
        logging.info("Transkribieren ...")
        path_to_audio = convert_to_audio(video_input)
        path, _ = os.path.splitext(path_to_audio)
        path_to_transcript = path + ".json"

        if os.path.exists(path_to_transcript):
            logging.info("Operation wurde bereits durchgeführt. Datei existiert bereits unter: " + path_to_transcript)
        else:
            try:
                transcript_response = self.whisper.transcribe(path_to_audio)
                with open(path_to_transcript, 'w', encoding='utf-8') as file:
                    json.dump(transcript_response, file, ensure_ascii=False, indent=4)
                logging.info("Erfolgreiche Transkription.")
            except Exception:
                raise Exception("Transkription fehlgeschlagen. Versuchen Sie den OpenAI-Server zu verwenden.")

        return path_to_transcript

    def chat(self, user_input, path_to_transcript, use_transcript, use_video):
        """
        Generates a chat response based on user input.
        Optionally including the transcript and video frames.
        """
        logging.info("Antworte auf Benutzereingabe ...")
        messages = "Du bist ein hilfreicher Assistent, der Fragen von Studenten zu Vorlesungen beantwortet. "
        if self.chat_history:
            messages += " Dies war der bisherige Chatverlauf:".join(self.chat_history)
            messages += " Ende des Chatverlaufs. Nun folgt die Frage."

        messages += self._add_content(path_to_transcript, use_transcript, use_video)

        if user_input:
            messages += f"USER: {user_input} ASSISTANT:"

        response = self.chatbot.generate(prompt=messages)
        self.chat_history.append(" USER: " + user_input)
        self.chat_history.append(" ASSISTANT: " + response)
        logging.info("Erfolgreich geantwortet.")
        return response

    def clear_chat(self):
        self.chat_history = []
        logging.info("Chat-Verlauf gelöscht.")

    def calculate_costs(self):
        return self.costs

    def _add_content(self, path_to_transcript, use_transcript, use_video):
        """
        Adds content to the user message based on the transcript and video frames if specified.
        """
        content = ""
        if use_transcript:
            if not os.path.exists(path_to_transcript):
                raise Exception("Das Transkript ist nicht verfügbar.")
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
            raise Exception("Der lokale Chatbot kann keine Videoabschnitte verarbeiten.")
        return content
