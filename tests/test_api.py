import unittest
from unittest.mock import patch, MagicMock
from backend.api import API


class TestAPI(unittest.TestCase):

    @patch("backend.api.load_dotenv")
    @patch("os.getenv")
    @patch("backend.api.OpenAI")
    def test_init(self, m_openai, m_getenv, m_load_dotenv):
        m_getenv.return_value = "your_api_key"
        api_instance = API()

        m_load_dotenv.assert_called_once()
        m_getenv.assert_called_once_with("OPENAI_API_KEY")
        m_openai.assert_called_once_with(api_key="your_api_key")
        self.assertEqual(api_instance.chat_history, [])
        self.assertEqual(api_instance.current_path, "")
        self.assertEqual(api_instance.video_frames_map, {})

    @patch("backend.api.convert_to_audio")
    @patch("builtins.open")
    @patch("json.dump")
    def test_transcribe(self, m_dump, m_open, m_convert_to_audio):
        m_convert_to_audio.return_value = "path/to/ABC.mp3"
        m_response = MagicMock()
        m_client = MagicMock()
        m_client.audio.transcriptions.create.return_value = m_response
        api_instance = API()
        api_instance.client = m_client

        result = api_instance.transcribe("https://youtube.com/watch?v=ABC")
        self.assertEqual(result, "path/to/ABC.json")
        m_convert_to_audio.assert_called_once_with("https://youtube.com/watch?v=ABC")
        m_client.audio.transcriptions.create.assert_called_once()
        m_open.assert_any_call("path/to/ABC.json", "w", encoding="utf-8")
        m_dump.assert_called_once()

    @patch("backend.api.API._add_transcript_to_context")
    @patch("backend.api.API._add_video_to_context")
    @patch("backend.api.log_api_response")
    def test_chat(self, m_log_api_response, m_add_video_to_context, m_add_transcript_to_context):
        m_response = MagicMock()
        m_client = MagicMock()
        m_client.chat.completions.create.return_value = m_response
        m_response.choices[0].message.content = "assistant_response_text"
        api_instance = API()
        api_instance.client = m_client
        api_instance.chat_history = [{"role": "system", "content": "hey"}]

        result = api_instance.chat("user_input", use_transcript=True, use_video=True)
        self.assertEqual(result, "assistant_response_text")
        m_add_transcript_to_context.assert_called_once()
        m_add_video_to_context.assert_called_once()
        m_client.chat.completions.create.assert_called_once()
        m_log_api_response.assert_called_once_with(m_response)
        self.assertIn({"role": "system", "content": "hey"}, api_instance.chat_history)
        self.assertIn({"role": "user", "content": "user_input"}, api_instance.chat_history)
        self.assertIn({"role": "assistant", "content": "assistant_response_text"}, api_instance.chat_history)

    def test_clear_chat(self):
        api_instance = API()
        api_instance.chat_history = [{"role": "user", "content": "hey"}]
        api_instance.clear_chat()
        self.assertEqual(api_instance.chat_history, [])

    @patch("os.path.exists")
    @patch("backend.api.open")
    @patch("json.load")
    @patch("backend.api.convert_seconds_to_hms")
    def test_add_transcript_to_context(self, m_convert_seconds_to_hms, m_load, m_open, m_exists):
        m_exists.return_value = True
        m_load.return_value = {"segments": [{"start": 0, "end": 1, "text": "hey"}]}
        api_instance = API()
        api_instance.current_path = "path/to/ABC"
        user_message = {"role": "user", "content": []}

        api_instance._add_transcript_to_context(user_message)
        m_exists.assert_any_call("path/to/ABC.json")
        m_open.assert_called_once_with("path/to/ABC.json", "r", encoding="utf-8")
        m_load.assert_called_once()
        m_convert_seconds_to_hms.assert_called()
        self.assertIn("Audiotranskription", user_message["content"][0]["text"])

    @patch("os.path.exists")
    @patch("backend.api.extract_video_frames")
    def test_add_video_to_context(self, m_extract_video_frames, m_exists):
        m_exists.return_value = True
        m_extract_video_frames.return_value = ["encoded_frame_0", "encoded_frame_1", "encoded_frame_2"]
        api_instance = API()
        api_instance.current_path = "path/to/ABC"
        user_message = {"role": "user", "content": []}

        api_instance._add_video_to_context(user_message)
        m_exists.assert_any_call("path/to/ABC.mp4")
        m_extract_video_frames.assert_called_once_with("path/to/ABC.mp4", api_instance.FRAME_INTERVAL_IN_SECONDS)
        self.assertEqual(len(user_message["content"]), 3)
        self.assertIn("encoded_frame_0", user_message["content"][0]["image_url"]["url"])
        self.assertIn("encoded_frame_1", user_message["content"][1]["image_url"]["url"])
        self.assertIn("encoded_frame_2", user_message["content"][2]["image_url"]["url"])


if __name__ == "__main__":
    unittest.main()