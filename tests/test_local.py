import unittest
from unittest.mock import patch, MagicMock
from backend.local import LOCAL


class TestLOCAL(unittest.TestCase):

    @patch("torch.cuda.is_available")
    @patch("whisper.load_model")
    @patch("backend.local.GPT4All")
    def test_init(self, m_gpt4all, m_load_model, m_is_available):
        m_is_available.return_value = True
        local_instance = LOCAL()

        m_is_available.assert_called_once_with()
        self.assertEqual(local_instance.chat_history, [])
        self.assertEqual(local_instance.costs, 0)
        m_load_model.assert_called_once_with(name=local_instance.MODEL_TRANSCRIBER, device="cuda")
        m_gpt4all.assert_called_once_with(model_name=local_instance.MODEL_CHATBOT)

    @patch("whisper.load_model")
    @patch("backend.local.GPT4All")
    @patch("backend.local.convert_to_audio")
    @patch("builtins.open")
    @patch("json.dump")
    def test_transcribe(self, m_dump, m_open, m_convert_to_audio, m_gpt4all, m_load_model):
        m_convert_to_audio.return_value = "path/to/ABC.mp3"
        m_transcribe = MagicMock(return_value={'text': 'transcript'})
        local_instance = LOCAL()
        local_instance.whisper.transcribe = m_transcribe

        result = local_instance.transcribe("https://youtube.com/watch?v=ABC")
        self.assertEqual(result, "path/to/ABC.json")
        m_convert_to_audio.assert_called_once_with("https://youtube.com/watch?v=ABC")
        m_transcribe.assert_called_once_with("path/to/ABC.mp3")
        m_open.assert_any_call("path/to/ABC.json", "w", encoding="utf-8")
        m_dump.assert_called_once()
        m_load_model.assert_called_once()
        m_gpt4all.assert_called_once()

    @patch("whisper.load_model")
    @patch("backend.local.GPT4All")
    @patch("backend.local.LOCAL._add_content")
    def test_chat(self, m_add_content, m_gpt4all, m_load_model):
        m_gpt4all.generate.return_value = "assistant_response_text"
        local_instance = LOCAL()
        local_instance.chatbot = m_gpt4all
        local_instance.chat_history = ["System: Start"]

        result = local_instance.chat("user_input", path_to_transcript="path/to/ABC.json", use_transcript=True,
                                     use_video=True)
        self.assertEqual(result, "assistant_response_text")
        m_add_content.assert_called_once()
        m_gpt4all.generate.assert_called_once()
        self.assertIn("System: Start", local_instance.chat_history)
        self.assertIn("Student: user_input", local_instance.chat_history)
        self.assertIn("Antwort: assistant_response_text", local_instance.chat_history)
        self.assertEqual(local_instance.costs, 0)
        m_load_model.assert_called_once()
        m_gpt4all.assert_called_once()

    @patch("whisper.load_model")
    @patch("backend.local.GPT4All")
    def test_clear_chat(self, m_gpt4all, m_load_model):
        local_instance = LOCAL()
        local_instance.chat_history = ["System: Start"]

        local_instance.clear_chat()
        self.assertEqual(local_instance.chat_history, [])
        m_load_model.assert_called_once()
        m_gpt4all.assert_called_once()

    @patch("whisper.load_model")
    @patch("backend.local.GPT4All")
    def test_calculate_costs(self, m_gpt4all, m_load_model):
        local_instance = LOCAL()

        result = local_instance.calculate_costs()
        self.assertEqual(result, 0)
        m_load_model.assert_called_once()
        m_gpt4all.assert_called_once()

    @patch("whisper.load_model")
    @patch("backend.local.GPT4All")
    @patch("os.path.exists")
    @patch("backend.local.open")
    @patch("json.load")
    @patch("backend.local.convert_seconds_to_hms")
    def test_add_content(self, m_convert_seconds_to_hms, m_load, m_open, m_exists, m_gpt4all, m_load_model):
        m_exists.return_value = True
        m_load.return_value = {"segments": [{"start": 0, "end": 1, "text": "hey"}]}
        local_instance = LOCAL()

        result = local_instance._add_content("path/to/ABC.json", use_transcript=True, use_video=False)
        m_exists.assert_any_call("path/to/ABC.json")
        m_open.assert_called_once_with("path/to/ABC.json", "r", encoding="utf-8")
        m_load.assert_called_once()
        m_convert_seconds_to_hms.assert_called()
        self.assertIn("Audiotranskription", result)
        m_load_model.assert_called_once()
        m_gpt4all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
