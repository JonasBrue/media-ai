from backend.api import API
from backend.local import LOCAL


class Model:
    """
    The Model class handles the data logic and interacts with the API.
    """

    def __init__(self):
        self.backends = {
            "api": API(),
            "local": LOCAL()
        }
        self.path_to_transcript = ""

    def transcribe(self, backend_id, video_input):
        """
        Transcribe audio from video input
        """
        if backend_id not in self.backends:
            raise Exception(f"Das Backend existiert nicht: {backend_id}")
        self.path_to_transcript = self.backends[backend_id].transcribe(video_input)

    def chat(self, backend_id, user_input, use_transcript, use_video):
        """
        Generate a chat response to the users input, optionally including the transcript and video.
        """
        if backend_id not in self.backends:
            raise Exception(f"Das Backend existiert nicht: {backend_id}")
        return self.backends[backend_id].chat(user_input, self.path_to_transcript, use_transcript, use_video)

    def clear_chat(self):
        """
        Clear the chat history
        """
        for backend in self.backends.values():
            backend.clear_chat()

    def calculate_costs(self):
        """
        Calculate costs
        """
        return sum(backend.calculate_costs() for backend in self.backends.values())
