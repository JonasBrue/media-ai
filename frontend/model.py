from backend.legacy.ytdownloader import YouTubeDownloader
from backend.legacy.asr import AutomaticSpeechRecognition
from backend.legacy.chatbot import ChatBot


class Model:
    def __init__(self):
        self.ytdownloader = YouTubeDownloader()
        self.asr = AutomaticSpeechRecognition()
        self.chatbot = ChatBot()

    def download(self, url):
        return self.ytdownloader.download(url)

    def transcribe(self, path_to_audio):
        return self.asr.transcribe(path_to_audio)

    def load(self, path_to_transcript):
        self.chatbot.load(path_to_transcript)

    def chat(self, prompt):
        return self.chatbot.chat(prompt)
