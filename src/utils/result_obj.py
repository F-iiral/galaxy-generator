import time
from PIL import Image

class Result:
    def __init__(self, ticks: float|None, image: Image.Image, *args):
        self.time = time.time() - ticks if ticks else None
        self.image = image
        self.data = args