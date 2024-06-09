import logging
from frontend.model import Model
from frontend.view import View
from frontend.controller import Controller

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s')

if __name__ == '__main__':
    view = View()
    model = Model()
    controller = Controller(view, model)
    view.mainloop()
