from pytube import YouTube
from openai import OpenAI
import pytube.exceptions
import urllib.error
import os
import whisper


def audio_from_youtube_video(url):
    try:
        yt = YouTube(url)  # A YouTube object with the url of the video to be downloaded.
        path_to_storage = "./temp/"
        path_to_audio = path_to_storage + yt.video_id + "-audio.mp3"

        if os.path.exists(path_to_audio):  # Check if the audio is already downloaded.
            print("Audio-File already exists at: " + path_to_audio)
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
    try:
        path_to_text = path_to_audio.replace("-audio.mp3", "-transcription.txt")

        if os.path.exists(path_to_text):  # Check if the transcription is already created.
            print("Text-File already exists at: " + path_to_text)
            return path_to_text

        print("Starting to transcribe, please wait...")
        model = whisper.load_model(model, device=device)  # Load a Whisper model
        result = model.transcribe(path_to_audio)  # Transcribe audio
        print("Transcription successful.")

        t = open(path_to_text, "w")
        t.write(result["text"])
        t.close()
        print("Saved to txt at: " + path_to_text)
        return path_to_text
    except:
        print("Transcription failed.")
        raise


def summarize_text(path_to_text):
    try:
        path_to_summary = path_to_text.replace("-transcription.txt", "-summary.txt")

        if os.path.exists(path_to_summary):  # Check if the summary is already created.
            print("Summary-File already exists at: " + path_to_summary)
            return path_to_summary

        print("Starting to summarize, please wait...")
        a = open("openai-api-key.txt", "r")
        api_key = a.readline()
        a.close()
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )
        s = open(path_to_summary, "w")
        s.write(completion.choices[0].message.content)
        s.close()
        print("Summary created.")

        print("Saved to txt at: " + path_to_summary)
        return path_to_summary
    except:
        print("Summary failed.")
        raise


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mp3 = audio_from_youtube_video("https://www.youtube.com/watch?v=bIgg91Mqd-k")
    # url: Insert Youtube video link

    txt = text_from_audio(mp3, "base", "cuda")
    # path_to_audio: mp3 file
    # model: tiny, base, small, medium or large
    # device: "cuda" to use the graphics card or "cpu" to use the processor

    smy = summarize_text(txt)
    # path_to_text: txt file

