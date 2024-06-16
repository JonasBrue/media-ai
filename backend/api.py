from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
from backend.utils import convert_to_audio, convert_seconds_to_hms, extract_video_frames, log_api_response


class API:
    MODEL_CHATBOT = "gpt-4o"
    MODEL_TRANSCRIBER = "whisper-1"
    EXTRACTED_FRAMES_AMOUNT = 10

    def __init__(self):
        """
        Loading environment variables and setting up the OpenAI client.
        """
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("API-Schlüssel nicht gefunden. Setzen den API-Schlüssel OPENAI_API_KEY in der .env-Datei.")
        self.client = OpenAI(api_key=api_key)
        self.chatbot_output_tokens_used = 0
        self.chatbot_input_tokens_used = 0
        self.transcriber_total_duration_in_seconds = 0
        self.chat_history = []
        self.video_frames_storage = {}
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
            transcript_response = self.client.audio.transcriptions.create(
                file=open(path_to_audio, "rb"),
                model=API.MODEL_TRANSCRIBER,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            transcript_data = {
                'task': transcript_response.task,
                'language': transcript_response.language,
                'duration': transcript_response.duration,
                'text': transcript_response.text,
                'segments': transcript_response.segments
            }
            with open(path_to_transcript, 'w', encoding='utf-8') as file:
                json.dump(transcript_data, file, ensure_ascii=False, indent=4)
            self.transcriber_total_duration_in_seconds += transcript_response.duration
            logging.info("Erfolgreiche Transkription.")

        return path_to_transcript

    def chat(self, user_input, path_to_transcript, use_transcript, use_video):
        """
        Generates a chat response based on user input.
        Optionally including the transcript and video frames.
        """
        logging.info("Antworte auf Benutzereingabe ...")

        messages = [{"role": "system", "content": "Sie sind ein hilfreicher Assistent, der Fragen von Studenten zu "
                                                  "Vorlesungen beantwortet. Ihnen können Bilder und ein Transkript "
                                                  "der Vorlesung zur Verfügung gestellt werden. "
                                                  "Bitte geben Sie präzise und verständliche Antworten, die den "
                                                  "Studenten helfen, die Inhalte der Vorlesung besser zu verstehen."}]
        if self.chat_history:
            messages.extend(self.chat_history)

        user_message = self._add_content(path_to_transcript, use_transcript, use_video)
        if user_input:
            user_message['content'].append({
                "type": "text",
                "text": f"{user_input}"
            })
        messages.append(user_message)

        response = self.client.chat.completions.create(
            model=API.MODEL_CHATBOT,
            messages=messages,
            temperature=0,
        )
        log_api_response(response)
        assistant_response = response.choices[0].message.content
        self.chat_history.append({"role": "user", "content": f"{user_input}"})
        self.chat_history.append({"role": "assistant", "content": f"{assistant_response}"})
        self.chatbot_output_tokens_used += response.usage.completion_tokens
        self.chatbot_input_tokens_used += response.usage.prompt_tokens
        logging.info("Erfolgreich geantwortet.")
        return assistant_response

    def clear_chat(self):
        self.chat_history = []
        logging.info("Chat-Verlauf gelöscht.")

    def calculate_costs(self):
        cost1 = self.chatbot_input_tokens_used * (5 / 1000000)  # 5,00 $ / 1M tokens
        cost2 = self.chatbot_output_tokens_used * (15 / 1000000)  # 15,00 $ / 1M tokens
        cost3 = self.transcriber_total_duration_in_seconds * (0.006 / 60)  # $0.006 / minute
        logging.info("Kosten berechnet.")
        return cost1 + cost2 + cost3

    def _add_content(self, path_to_transcript, use_transcript, use_video):
        """
        Adds content to the user message based on the transcript and video frames if specified.
        """
        user_message = {"role": "user", "content": []}
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
            user_message['content'].append({
                "type": "text",
                "text": f"Die Audiotranskription der Vorlesung ist: \n{transcript_formatted}"
            })
        if use_video:
            path, _ = os.path.splitext(path_to_transcript)
            path_to_video = path + ".mp4"
            if not os.path.exists(path_to_video):
                raise Exception("Das Video ist nicht verfügbar.")
            if path_to_video not in self.video_frames_storage:
                self.video_frames_storage[path_to_video] = extract_video_frames(path_to_video, API.EXTRACTED_FRAMES_AMOUNT)
            user_message['content'].extend([
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f'data:image/jpg;base64,{frame}',
                        "detail": "low"
                    }
                } for frame in self.video_frames_storage[path_to_video]
            ])
        return user_message
