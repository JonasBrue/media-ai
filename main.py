from pytube import YouTube
import os


def mp3_from_youtube_video(url):
    path_to_storage = "./temp/audio/"

    try:
        yt = YouTube(url)  # A YouTube object with the url of the video to be downloaded.
        path_to_file = path_to_storage + yt.video_id + ".mp3"
        print("Found video: '" + yt.title + "' by '" + yt.author + "'")
    except:
        print("Incorrect input or internet connection not possible.")  # to handle exception

    try:
        if os.path.exists(path_to_file):  # Check if the mp3 is already downloaded.
            print("File already exists at: " + path_to_file)
        else:
            audio = yt.streams.filter(only_audio=True, file_extension="mp4").last()  # Find a stream that only has audio

            print("Starting to download, please wait...")
            download = audio.download(output_path=path_to_storage)
            print("Download successful.")

            os.rename(download, path_to_file)  # Turn the file into a mp3 file
            print("Converted to mp3 at: " + path_to_file)
        return path_to_file
    except:
        print("Download failed. Check your internet connection.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mp3 = mp3_from_youtube_video("")
