from pytube import YouTube
import pytube.exceptions
import urllib.error
import os


def mp3_from_youtube_video(url):
    try:
        yt = YouTube(url)  # A YouTube object with the url of the video to be downloaded.
        path_to_storage = "./temp/audio/"
        path_to_file = path_to_storage + yt.video_id + ".mp3"

        if os.path.exists(path_to_file):  # Check if the mp3 is already downloaded.
            print("File already exists at: " + path_to_file)
            return path_to_file

        audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").last()  # Find a stream that only has audio
        print("Found video: '" + yt.title + "' by '" + yt.author + "'")

        print("Starting to download, please wait...")
        download = audio_stream.download(output_path=path_to_storage)
        print("Download successful.")

        os.rename(download, path_to_file)  # Turn the file into a mp3 file
        print("Converted to mp3 at: " + path_to_file)
        return path_to_file
    except urllib.error.URLError:
        print("No internet connection.")
        raise
    except pytube.exceptions.RegexMatchError:
        print("Incorrect input.")
        raise
    except pytube.exceptions.VideoUnavailable:
        print("Video Unavailable.")
        raise


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mp3 = mp3_from_youtube_video("")
