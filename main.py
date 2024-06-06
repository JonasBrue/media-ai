import logging
from modules.ytdownloader import YouTubeDownloader
from modules.asr import AutomaticSpeechRecognition
from modules.chatbot import ChatBot

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s')

if __name__ == '__main__':
    url = "https://www.youtube.com/watch?v=UQLcm8Zw8DM"
    path_to_audio = YouTubeDownloader(url).download()
    path_to_transcript = AutomaticSpeechRecognition().transcribe(path_to_audio)
    userinput = "Sag mir in einem Satz worum es in diesem Video/Transkript geht."
    path_to_summary = ChatBot(path_to_transcript).chat(userinput)
