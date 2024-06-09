from openai import OpenAI
from moviepy.editor import AudioFileClip
import datetime
import json
import os
import logging


class API:

    def __init__(self):
        logging.info("Starting ...")
        key = open("../keys/openai-api-key.txt", "r")
        self.client = OpenAI(api_key=key.readline())
        self.model_chatbot = "gpt-4o"
        self.model_transcriber = "whisper-1"
        logging.info("Started.")

    def convert_to_audio(self, path_to_video):
        logging.info("Converting video to audio ...")

        path_to_audio = path_to_video.replace("-video.mp4", "-audio.mp3")
        if os.path.exists(path_to_audio):
            logging.info("Operation done before. File already exists at: " + path_to_audio)
        else:
            video = AudioFileClip(path_to_video)
            video.write_audiofile(path_to_audio)
            video.close()
            logging.info("Converting successful.")

        return path_to_audio

    def transcribe(self, path_to_audio):
        logging.info("Transcribing the audio ...")

        path_to_transcript = path_to_audio.replace("-audio.mp3", "-transcript.json")
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

    def chat(self, userinput, path_to_transcript):
        logging.info("Responding to user input ...")

        with open(path_to_transcript, 'r', encoding='utf-8') as file:
            transcript = json.load(file)

        completion = self.client.chat.completions.create(
            model=self.model_chatbot,
            messages=[
                {"role": "system", "content": """Sie beantworten Fragen von Studenten zu Vorlesungen. Die Audiotranskription wird bereitgestellt."""},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Die Audiotranskription ist: {transcript['text']} \n\n\n {userinput}"}
                    ]
                }
            ],
            temperature=0,
        )
        log_api_response(completion)
        logging.info("Responding successful.")
        return completion.choices[0].message.content

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s')

# Testing
if __name__ == '__main__':
    api = API()
    audio = api.convert_to_audio("..\storage\k-video.mp4")
    transcript = api.transcribe(audio)
    response = api.chat("Worum geht es in dieser Vorlesung?", transcript)
    print(response)


# Helper
def log_api_response(completion):
    completion_data = {
        'id': completion.id,
        'choices': [
            {
                'finish_reason': choice.finish_reason,
                'index': choice.index,
                'logprobs': choice.logprobs,
                'message': {
                    'content': choice.message.content,
                    'role': choice.message.role,
                    'function_call': choice.message.function_call,
                    'tool_calls': choice.message.tool_calls
                }
            } for choice in completion.choices
        ],
        'created': completion.created,
        'model': completion.model,
        'object': completion.object,
        'system_fingerprint': completion.system_fingerprint,
        'usage': {
            'completion_tokens': completion.usage.completion_tokens,
            'prompt_tokens': completion.usage.prompt_tokens,
            'total_tokens': completion.usage.total_tokens
        }
    }
    path_to_log = "../storage/api-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".json"
    with open(path_to_log, 'w', encoding='utf-8') as file:
        json.dump(completion_data, file, ensure_ascii=False, indent=4)