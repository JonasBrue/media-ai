from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
from backend.utils import convert_to_audio, convert_seconds_to_hms, extract_video_frames, log_api_response


class API:
    MODEL_CHATBOT = "gpt-4o"
    MODEL_TRANSCRIBER = "whisper-1"
    FRAME_INTERVAL_IN_SECONDS = 10

    def __init__(self):
        """
        Loading environment variables and setting up the OpenAI client.
        """
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("API key not found. Set the OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key)
        self.chatbot_output_tokens_used = 0
        self.chatbot_input_tokens_used = 0
        self.transcriber_total_duration_in_seconds = 0
        self.chat_history = []
        self.current_path = ""
        self.video_frames_map = {}
        logging.info("Started.")

    def transcribe(self, video_input):
        """
        Transcribes the audio from a given video input.
        Converts video to audio and then transcribes the audio.
        Returns the path to the transcript JSON file.
        """
        logging.info("Transcribing ...")
        path_to_audio = convert_to_audio(video_input)
        self.current_path, _ = os.path.splitext(path_to_audio)

        path_to_transcript = self.current_path + ".json"
        if os.path.exists(path_to_transcript):
            logging.info("Operation done before. File already exists at: " + path_to_transcript)
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
            logging.info("Transcribing successful.")

        return path_to_transcript

    def chat(self, user_input, use_transcript, use_video):
        """
        Generates a chat response based on user input.
        Optionally including the transcript and video frames.
        """
        logging.info("Responding to user input ...")

        messages = [{"role": "system", "content": "Sie sind ein hilfreicher Assistent, der Fragen von Studenten zu "
                                                  "Vorlesungen beantwortet. Ihnen können Bilder und ein Transkript "
                                                  "der Vorlesung zur Verfügung gestellt werden. "
                                                  "Bitte geben Sie präzise und verständliche Antworten, die den "
                                                  "Studenten helfen, die Inhalte der Vorlesung besser zu verstehen."}]
        if self.chat_history:
            messages.extend(self.chat_history)

        user_message = {"role": "user", "content": []}
        if use_transcript:
            self._add_transcript_to_context(user_message)
        if use_video:
            self._add_video_to_context(user_message)
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
        logging.info("Responding successful.")
        return assistant_response

    def clear_chat(self):
        self.chat_history = []
        logging.info("Chat history cleared.")

    def calculate_costs(self):
        cost1 = self.chatbot_input_tokens_used * (5/1000000)   # 5,00 $ / 1M tokens
        cost2 = self.chatbot_output_tokens_used * (15/1000000)  # 15,00 $ / 1M tokens
        cost3 = self.transcriber_total_duration_in_seconds * (0.006/60)  # $0.006 / minute
        logging.info("Costs calculated.")
        return cost1 + cost2 + cost3

    def _add_transcript_to_context(self, user_message):
        """
        Adds the formatted transcript of the audio to the context of the user message.
        """
        if not os.path.exists(self.current_path + ".json"):
            raise Exception("Transcript is not available.")
        with open(self.current_path + ".json", 'r', encoding='utf-8') as file:
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

    def _add_video_to_context(self, user_message):
        """
        Adds encoded video frames to the context of the user message and saves them in a map.
        """
        if not os.path.exists(self.current_path + ".mp4"):
            raise Exception("Video is not available.")
        if self.current_path not in self.video_frames_map:
            self.video_frames_map[self.current_path] = extract_video_frames(self.current_path + ".mp4", API.FRAME_INTERVAL_IN_SECONDS)
        user_message['content'].extend([
            {
                "type": "image_url",
                "image_url": {
                    "url": f'data:image/jpg;base64,{frame}',
                    "detail": "low"
                }
            } for frame in self.video_frames_map[self.current_path]
        ])
