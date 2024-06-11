import logging
from backend.api import API

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s')

# if __name__ == '__main__':
#    view = View()
#    model = Model()
#    controller = Controller(view, model)
#    view.mainloop()

# Testing
if __name__ == '__main__':
    api = API()
    transcriptYT = api.transcribe("https://www.youtube.com/watch?v=BE-L7xu8pO4")
    print(api.chat("Worum geht es in dem Video", use_video=True))
    print(api.chat("Welche Farbe haben die Wörter: import, def, in dem Video?", use_video=True))
    api.reset_cache()
    transcriptMP4 = api.transcribe("./storage/kapitalismus.mp4")
    print(api.chat("Warum wird der Kapitalismus laut der Vorlesung heute stark kritisiert?", use_transcript=True))
    print(api.chat("Was waren meine vorherigen Fragen? Gib sie exakt weider."))
    print(api.get_chat_history())
