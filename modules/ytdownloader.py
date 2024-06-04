import urllib
import pytube
import os
import logging


class YouTubeDownloader:

    def __init__(self, url):
        """
        Initializes the YouTubeDownloader instance with the url of the video to be downloaded.

        Parameters:
        url (str): The URL of the YouTube video to be downloaded.
        """
        try:
            self.yt = pytube.YouTube(url)
        except pytube.exceptions.RegexMatchError:
            logging.error("Incorrect input.")
            raise
        self.path_to_storage = "./storage/"
        self.path_to_audio = self.path_to_storage + self.yt.video_id + "-audio.mp3"
        logging.info("Module: YouTubeDownloader initialized.")

    def download(self):
        """
        Downloads the audio from the YouTube video if it doesn't already exist.

        Returns:
        str: The path to the downloaded audio file.
        """
        if os.path.exists(self.path_to_audio):
            logging.info("Audio-File already exists at: " + self.path_to_audio)
            return self.path_to_audio

        try:
            logging.info("Looking for the video on youtube...")
            stream = self.yt.streams.filter(only_audio=True, file_extension="mp4").last()
            logging.info("Found video: '" + self.yt.title + "' by '" + self.yt.author + "'")
            logging.info("Starting to download, please wait...")
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