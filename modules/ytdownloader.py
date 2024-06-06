import urllib
import pytube
import os
import logging


class YouTubeDownloader:

    def __init__(self, url):
        logging.info("Starting ...")

        try:
            self.yt = pytube.YouTube(url)
        except pytube.exceptions.RegexMatchError:
            logging.error("Incorrect input.")
            raise
        self.path_to_storage = "./storage/"
        self.path_to_audio = self.path_to_storage + self.yt.video_id + "-audio.mp3"

        logging.info("Started.")

    def download(self):
        logging.info("Downloading ...")

        if os.path.exists(self.path_to_audio):
            logging.info("Audio-File already exists at: " + self.path_to_audio)
            return self.path_to_audio

        try:
            logging.info("Looking for the video on youtube ...")
            stream = self.yt.streams.filter(only_audio=True, file_extension="mp4").last()
            logging.info("Found video: '" + self.yt.title + "' by '" + self.yt.author + "'")
            logging.info("Starting to download ...")
            download = stream.download(output_path=self.path_to_storage)
            logging.info("Download successful.")
        except urllib.error.URLError:
            logging.error("No internet connection.")
            raise
        except pytube.exceptions.VideoUnavailable:
            logging.error("Video Unavailable.")
            raise

        os.rename(download, self.path_to_audio)  # Turn the mp4 file into a mp3 file
        logging.info("Converted to mp3 file at: " + self.path_to_audio)
        return self.path_to_audio