from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
from backend.utils import convert_to_audio, extract_video_frames, log_api_response

# Load environment variables from .env file
load_dotenv()


class API:

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("API key not found. Set the OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key)
        self.model_chatbot = "gpt-4o"
        self.model_transcriber = "whisper-1"
        self.file_path = ""
        self.chat_history = []
        self.video_frames = []
        logging.info("Started.")

    def reset_cache(self):
        self.file_path = ""
        self.chat_history = []
        self.video_frames = []
        logging.info("Chat history cleared.")

    def get_chat_history(self):
        return self.chat_history

    def transcribe(self, video_input):
        """
        Transcribes a given video file or YouTube video.
        """
        logging.info("Transcribing ...")
        path_to_audio = convert_to_audio(video_input)
        self.file_path, _ = os.path.splitext(path_to_audio)

        path_to_transcript = self.file_path + ".json"
        if os.path.exists(path_to_transcript):
            logging.info("Operation done before. File already exists at: " + path_to_transcript)
        else:
            transcript_response = self.client.audio.transcriptions.create(
                file=open(path_to_audio, "rb"),
                model=self.model_transcriber,
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
            logging.info("Transcribing successful.")

        return path_to_transcript

    def chat(self, user_input, use_transcript=False, use_video=False, frame_interval_in_seconds=10):
        logging.info("Responding to user input ...")

        messages = [{"role": "system", "content": "Sie beantworten Fragen von Studenten zu Vorlesungen."}]

        if self.chat_history:
            messages.extend(self.chat_history)

        user_message = {"role": "user", "content": []}

        if use_transcript:
            if not os.path.exists(self.file_path + ".json"):
                raise Exception("Transcript is not available.")
            with open(self.file_path + ".json", 'r', encoding='utf-8') as file:
                transcript = json.load(file)
            transcript_text = transcript['text']
            user_message['content'].append({
                "type": "text",
                "text": f"Die Audiotranskription der Vorlesung ist: {transcript_text}"
            })

        if use_video:
            if not os.path.exists(self.file_path + ".mp4"):
                raise Exception("Video is not available.")
            if not self.video_frames:
                self.video_frames = extract_video_frames(self.file_path + ".mp4", frame_interval_in_seconds)
            user_message['content'].append({
                "type": "text",
                "text": "Dies sind die Bilder aus dem Video."
            })
            user_message['content'].extend([
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f'data:image/jpg;base64,{frame}',
                        "detail": "low"
                    }
                } for frame in self.video_frames
            ])

        if user_input:
            user_message['content'].append({
                "type": "text",
                "text": f"{user_input}"
            })

        messages.append(user_message)

        response = self.client.chat.completions.create(
            model=self.model_chatbot,
            messages=messages,
            temperature=0,
        )
        log_api_response(response)
        assistant_response = response.choices[0].message.content
        self.chat_history.append({"role": "user", "content": f"{user_input}"})
        self.chat_history.append({"role": "assistant", "content": f"{assistant_response}"})
        logging.info("Responding successful.")
        return assistant_response
