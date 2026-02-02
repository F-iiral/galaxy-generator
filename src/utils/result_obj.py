import time
from PIL import Image

class Result:
    def __init__(self, ticks: float, image: Image.Image, *args):
        self.time = time.time() - ticks
        self.image = image
        self.data = args