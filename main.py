from frontend.controller import Controller
from frontend.model import Model
from frontend.view import View
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s')

# Initialize MVC components
if __name__ == '__main__':
    view = View()
    model = Model()
    controller = Controller(view, model)
    view.mainloop()
