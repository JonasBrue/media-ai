from pytube import YouTube
import pytube.exceptions
import urllib.error
import os
import whisper


def audio_from_youtube_video(url):
    try:
        yt = YouTube(url)  # A YouTube object with the url of the video to be downloaded.
        path_to_storage = "./temp/"
        path_to_audio = path_to_storage + yt.video_id + ".mp3"

        if os.path.exists(path_to_audio):  # Check if the mp3 is already downloaded.
            print("File already exists at: " + path_to_audio)
            return path_to_audio

        stream = yt.streams.filter(only_audio=True, file_extension="mp4").last()  # Find a stream that only has audio
        print("Found video: '" + yt.title + "' by '" + yt.author + "'")

        print("Starting to download, please wait...")
        download = stream.download(output_path=path_to_storage)
        print("Download successful.")

        os.rename(download, path_to_audio)  # Turn the file into a mp3 file
        print("Converted to mp3 at: " + path_to_audio)
        return path_to_audio
    except urllib.error.URLError:
        print("No internet connection.")
        raise
    except pytube.exceptions.RegexMatchError:
        print("Incorrect input.")
        raise
    except pytube.exceptions.VideoUnavailable:
        print("Video Unavailable.")
        raise


def text_from_audio(path_to_audio, model, device):
    model = whisper.load_model(model, device=device)  # Load a Whisper model

    result = model.transcribe(path_to_audio)
    return result["text"]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mp3 = audio_from_youtube_video("")
    # Url: Insert Youtube video link

    txt = text_from_audio(mp3, "base", "cuda")
    # Model: tiny, base, small, medium or large
    # Device: "cuda" to use the graphics card or "cpu" to use the processor

    print(txt)
