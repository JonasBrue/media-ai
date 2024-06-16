import unittest
from unittest.mock import patch, MagicMock
import base64
import datetime
from backend.utils import (
    convert_to_audio, video_to_audio, download_youtube_video,
    convert_seconds_to_hms, extract_video_frames, log_api_response
)


class TestUtils(unittest.TestCase):

    @patch("backend.utils.download_youtube_video")
    @patch("backend.utils.video_to_audio")
    def test_convert_to_audio_input_youtube(self, m_video_to_audio, m_download_youtube_video):
        m_download_youtube_video.return_value = "path/to/youtube-ABC.mp4"
        m_video_to_audio.return_value = "path/to/youtube-ABC.mp3"

        result = convert_to_audio("https://youtube.com/watch?v=ABC")
        self.assertEqual(result, "path/to/youtube-ABC.mp3")
        m_download_youtube_video.assert_called_once_with("https://youtube.com/watch?v=ABC")
        m_video_to_audio.assert_called_once_with("path/to/youtube-ABC.mp4")

    @patch("os.path.exists")
    @patch("backend.utils.video_to_audio")
    def test_convert_to_audio_input_file(self, m_video_to_audio, m_exists):
        m_exists.return_value = True
        m_video_to_audio.return_value = "path/to/ABC.mp3"

        result = convert_to_audio("path/to/ABC.mp4")
        self.assertEqual(result, "path/to/ABC.mp3")
        m_exists.assert_called_once_with("path/to/ABC.mp4")
        m_video_to_audio.assert_called_once_with("path/to/ABC.mp4")

    @patch("os.path.exists")
    @patch("backend.utils.AudioFileClip")
    def test_video_to_audio(self, m_audio_file_clip, m_exists):
        m_exists.return_value = False
        m_video = m_audio_file_clip.return_value
        m_video.write_audiofile.return_value = None

        result = video_to_audio("path/to/ABC.mp4")
        self.assertEqual(result, "path/to/ABC.mp3")
        m_exists.assert_called_once_with("path/to/ABC.mp3")
        m_audio_file_clip.assert_called_once_with("path/to/ABC.mp4")
        m_video.write_audiofile.assert_called_once_with("path/to/ABC.mp3")
        m_video.close.assert_called_once_with()

    @patch("pytube.YouTube")
    @patch("os.path.exists")
    @patch("os.rename")
    def test_download_youtube_video(self, m_rename, m_exists, m_youtube):
        m_exists.return_value = False
        m_yt = m_youtube.return_value
        m_yt.video_id = "ABC"
        m_stream = m_yt.streams.filter.return_value.get_highest_resolution.return_value
        m_stream.download.return_value = "path/to/name_of_video.mp4"

        result = download_youtube_video("https://www.youtube.com/watch?v=ABC")
        self.assertEqual(result, "./storage/youtube-ABC.mp4")
        m_youtube.assert_called_once_with("https://www.youtube.com/watch?v=ABC")
        m_exists.assert_called_once_with("./storage/youtube-ABC.mp4")
        m_rename.assert_called_once_with("path/to/name_of_video.mp4", "./storage/youtube-ABC.mp4")

    def test_convert_seconds_to_hms(self):
        self.assertEqual(convert_seconds_to_hms(5025), "1:23:45")
        self.assertEqual(convert_seconds_to_hms(3723), "1:02:03")
        self.assertEqual(convert_seconds_to_hms(81), "1:21")
        self.assertEqual(convert_seconds_to_hms(37), "0:37")
        self.assertEqual(convert_seconds_to_hms(1), "0:01")
        self.assertEqual(convert_seconds_to_hms(0), "0:00")

    @patch("cv2.VideoCapture")
    def test_extract_video_frames(self, m_video_capture):
        TOTAL_FRAMES = 20
        EXTRACTED_FRAMES_AMOUNT = 2
        FRAME_INTERVAL = TOTAL_FRAMES // EXTRACTED_FRAMES_AMOUNT
        OFFSET = FRAME_INTERVAL // 2
        m_video = m_video_capture.return_value
        m_video.get.return_value = TOTAL_FRAMES
        m_video.read.side_effect = [(True, f"frame_{i}") for i in range(TOTAL_FRAMES)] + [(False, "None")]
        m_encode = patch("cv2.imencode", return_value=(True, b"encoded_frame")).start()
        expected_encoding_of_frames = base64.b64encode(b"encoded_frame").decode("utf-8")
        expected_result = []
        for i in range(OFFSET, TOTAL_FRAMES, FRAME_INTERVAL):
            if i < TOTAL_FRAMES:
                expected_result.append(expected_encoding_of_frames)
            if len(expected_result) >= EXTRACTED_FRAMES_AMOUNT:
                break

        result = extract_video_frames("path/to/video.mp4", EXTRACTED_FRAMES_AMOUNT)
        self.assertEqual(result, expected_result)
        m_video_capture.assert_called_once_with("path/to/video.mp4")
        m_video.get.assert_called_once()
        m_video.isOpened.assert_called()
        m_video.release.assert_called_once_with()
        m_encode.assert_called()

    @patch("backend.utils.datetime")
    @patch("builtins.open")
    @patch("backend.utils.json.dump")
    @patch("backend.utils.logging.info")
    def test_log_api_response(self, m_info, m_dump, m_open, m_datetime):
        m_datetime.datetime.now.return_value = datetime.datetime(2000, 1, 1, 1, 0, 0)
        m_datetime.datetime.strftime.return_value = "2000-01-01-01-00-00"
        m_completion = MagicMock()
        m_completion.id = "test_mock_id"
        m_completion.choices = [
            MagicMock(
                finish_reason="test_mock_reason",
                index=123,
                logprobs=None,
                message=MagicMock(
                    content="test_mock_content",
                    role="test_mock_role",
                    function_call=None,
                    tool_calls=None
                )
            )
        ]
        m_completion.created = 42
        m_completion.model = "test_mock_model"
        m_completion.object = "test_mock_object"
        m_completion.system_fingerprint = "test_mock_fingerprint"
        m_completion.usage = MagicMock(
            completion_tokens=1,
            prompt_tokens=2,
            total_tokens=3
        )
        expected_data = {
            "id": "test_mock_id",
            "choices": [
                {
                    "finish_reason": "test_mock_reason",
                    "index": 123,
                    "logprobs": None,
                    "message": {
                        "content": "test_mock_content",
                        "role": "test_mock_role",
                        "function_call": None,
                        "tool_calls": None
                    }
                }
            ],
            "created": 42,
            "model": "test_mock_model",
            "object": "test_mock_object",
            "system_fingerprint": "test_mock_fingerprint",
            "usage": {
                "completion_tokens": 1,
                "prompt_tokens": 2,
                "total_tokens": 3
            }
        }
        log_api_response(m_completion)

        m_open.assert_called_once_with("./log/api-response-2000-01-01-01-00-00.json", "w", encoding="utf-8")
        m_dump.assert_called_once_with(expected_data, m_open().__enter__(), ensure_ascii=False, indent=4)
        m_info.assert_called_once_with("API-Antwort gespeichert unter: ./log/api-response-2000-01-01-01-00-00.json")


if __name__ == "__main__":
    unittest.main()
