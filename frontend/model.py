from backend.api import API
from backend.local import LOCAL


class Model:
    """
    The Model class handles the data logic and interacts with the API.
    """

    def __init__(self):
        self.backends = {
            True: API(),
            False: LOCAL()
        }
        self.path_to_transcript = ""

    def transcribe(self, use_api, video_input):
        """
        Transcribe audio from video input
        """
        self.path_to_transcript = self.backends[use_api].transcribe(video_input)

    def chat(self, use_api, user_input, use_transcript, use_video):
        """
        Generate a chat response to the users input, optionally including the transcript and video.
        """
        return self.backends[use_api].chat(user_input, self.path_to_transcript, use_transcript, use_video)

    def clear_chat(self, use_api):
        """
        Clear the chat history
        """
        self.backends[use_api].clear_chat()

    def calculate_costs(self):
        """
        Calculate costs
        """
        return sum(backend.calculate_costs() for backend in self.backends.values())
