import urllib
import pytube
import os
import logging


class YouTubeDownloader:

    def __init__(self):
        logging.info("Starting ...")

        logging.info("Started.")

    def download(self, url):
        logging.info("Downloading ...")

        try:
            yt = pytube.YouTube(url)
        except pytube.exceptions.RegexMatchError:
            logging.error("Incorrect input.")
            raise
        path_to_storage = "./storage/"
        path_to_audio = path_to_storage + yt.video_id + "-audio.mp3"

        if os.path.exists(path_to_audio):
            logging.info("Audio-File already exists at: " + path_to_audio)
            return path_to_audio

        try:
            logging.info("Looking for the video on youtube ...")
            stream = yt.streams.filter(only_audio=True, file_extension="mp4").last()
            logging.info("Found video: '" + yt.title + "' by '" + yt.author + "'")
            logging.info("Starting to download ...")
            download = stream.download(output_path=path_to_storage)
            logging.info("Download successful.")
        except urllib.error.URLError:
            logging.error("No internet connection.")
            raise
        except pytube.exceptions.VideoUnavailable:
            logging.error("Video Unavailable.")
            raise

        os.rename(download, path_to_audio)  # Turn the mp4 file into a mp3 file
        logging.info("Converted to mp3 file at: " + path_to_audio)
        return path_to_audio
