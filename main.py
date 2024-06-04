import logging
from modules.ytdownloader import YouTubeDownloader
from modules.asr import AutomaticSpeechRecognition
from modules.chatbot import ChatBot

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    url = "https://www.youtube.com/watch?v=CmKR5AXf33A"
    path_to_audio = YouTubeDownloader(url).download()
    path_to_transcript = AutomaticSpeechRecognition(path_to_audio).transcribe()
    path_to_summary = ChatBot(path_to_transcript).summarize()
