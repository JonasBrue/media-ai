import pytube
from pytube.exceptions import RegexMatchError, VideoUnavailable
from urllib.error import URLError
from moviepy.editor import AudioFileClip
import cv2
import base64
import datetime
import json
import os
import logging


def convert_to_audio(user_input):
    """
    Converts the video input to a valid audio format, either by downloading from YouTube or converting video to audio.
    """
    if "youtube.com" in user_input or "youtu.be" in user_input:
        path_to_video = download_youtube_video(user_input)
        return video_to_audio(path_to_video)
    elif os.path.exists(user_input):
        if user_input.lower().endswith('.mp4'):
            return video_to_audio(user_input)
        else:
            raise Exception("Unsupported file format. Please provide an .mp4 file or a YouTube url.")
    else:
        raise Exception("Input does not exist.")


def video_to_audio(path_to_video):
    """
    Converts a video file to an audio file.
    """
    logging.info("Converting video to audio ...")
    path_to_audio = path_to_video.replace(".mp4", ".mp3")

    if os.path.exists(path_to_audio):
        logging.info("Operation done before. File already exists at: " + path_to_audio)
    else:
        video = AudioFileClip(path_to_video)
        video.write_audiofile(path_to_audio)
        video.close()
        logging.info("Converted to mp3 file at: " + path_to_audio)

    return path_to_audio


def download_youtube_video(url):
    """
    Downloads the audio from a YouTube video.
    """
    try:
        yt = pytube.YouTube(url)
    except RegexMatchError:
        raise Exception("Incorrect input.")

    path_to_storage = "../storage/"
    path_to_video = path_to_storage + "youtube-" + yt.video_id + ".mp4"
    if os.path.exists(path_to_video):
        logging.info("Operation done before. File already exists at: " + path_to_video)
        return path_to_video

    try:
        logging.info("Looking for the video on youtube ...")
        stream = yt.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
        logging.info("Found video: '" + yt.title + "' by '" + yt.author + "'")
        logging.info("Starting to download ...")
        download = stream.download(output_path=path_to_storage)
        logging.info("Download successful.")
    except VideoUnavailable:
        raise Exception("Video Unavailable.")
    except URLError:
        raise Exception("No internet connection.")

    os.rename(download, path_to_video)  # Save the mp4 file in storage
    logging.info("Converted to mp4 file at: " + path_to_video)
    return path_to_video


def extract_video_frames(path_to_video, interval_seconds):
    """
    Extracts frames from a video at specified intervals and encodes them to base64.
    """
    logging.info(f"Extracting video frames ...")
    video = cv2.VideoCapture(path_to_video)
    video_frames = []

    # Calculating the amount of frames to skip between each extraction
    frame_per_seconds = video.get(cv2.CAP_PROP_FPS)  # FPS
    frame_interval = frame_per_seconds * interval_seconds

    frame_count = 0
    while video.isOpened():
        # Read frames until the end of file
        successful_read, frame = video.read()
        if not successful_read:
            break
        if frame_count % frame_interval == 0:
            # Save frame as JPEG and encode to base64
            successful_encode, buffer = cv2.imencode('.jpg', frame)
            if successful_encode:
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                video_frames.append(frame_base64)
        frame_count += 1
    video.release()

    logging.info(f"Extracted {len(video_frames)} frames")
    return video_frames


def log_api_response(completion):
    """
    Logs the API response to a JSON file.
    """
    completion_data = {
        'id': completion.id,
        'choices': [
            {
                'finish_reason': choice.finish_reason,
                'index': choice.index,
                'logprobs': choice.logprobs,
                'message': {
                    'content': choice.message.content,
                    'role': choice.message.role,
                    'function_call': choice.message.function_call,
                    'tool_calls': choice.message.tool_calls
                }
            } for choice in completion.choices
        ],
        'created': completion.created,
        'model': completion.model,
        'object': completion.object,
        'system_fingerprint': completion.system_fingerprint,
        'usage': {
            'completion_tokens': completion.usage.completion_tokens,
            'prompt_tokens': completion.usage.prompt_tokens,
            'total_tokens': completion.usage.total_tokens
        }
    }
    path_to_log = "../storage/api-response-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".json"
    with open(path_to_log, 'w', encoding='utf-8') as file:
        json.dump(completion_data, file, ensure_ascii=False, indent=4)
    logging.info("Saved api response at: " + path_to_log)
