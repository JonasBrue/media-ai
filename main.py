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


def text_from_audio(path_to_audio, model):
    model = whisper.load_model(model)  # Load a Whisper model

    # try to transcribe
    # result = model.transcribe(path_to_audio, fp16=False)
    # print(result)

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(mp3)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)
    print(f"Detected language: {language}")

    # decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)

    return result.text


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mp3 = audio_from_youtube_video("")  # Insert Youtube video link
    txt = text_from_audio(mp3, "base")  # Model: tiny, base, small, medium or large

    print(txt)
