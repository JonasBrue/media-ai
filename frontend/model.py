from backend.api import API


class Model:
    """
    The Model class handles the data logic and interacts with the API.
    """
    def __init__(self):
        self.api = API()

    def transcribe(self, video_input):
        """
        Transcribe audio from video input
        """
        return self.api.transcribe(video_input)

    def chat(self, user_input, use_transcript, use_video):
        """
        Generate a chat response to the users input, optionally including the transcript and video.
        """
        return self.api.chat(user_input, use_transcript, use_video)

    def clear_chat(self):
        """
        Clear the chat history
        """
        self.api.clear_chat()

    def calculate_costs(self):
        """
        Calculate costs
        """
        return self.api.calculate_costs()
