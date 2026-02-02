import time
import random
import math
from src.utils.result_obj import Result
from src.utils.settings import Settings
from PIL import Image, ImageDraw, ImageFilter

def generate_background(settings: Settings, size: int, center: int) -> Result:
    start_time = time.time()
    bk = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    core_glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(core_glow)

    # Draw multiple concentric circles with decreasing opacity
    for r in range(size // 10, 0, -2):
        alpha = int(100 * (1 - r / (size // 10)))
        draw.ellipse([center-r, center-r, center+r, center+r], fill=(255, 240, 200, min(alpha*2,255)))

    # Disk is big
    nebula_count = 50000 * size * size // (2000 * 2000)
    radius = size / 2
    for _ in range(nebula_count):
        theta = random.random() * 2 * math.pi
        r = radius * random.random() ** 0.7
        x = center + r * math.cos(theta)
        y = center + r * math.sin(theta)

        if 0 <= x < size and 0 <= y < size:
            draw.circle([x, y], radius=5, fill=(150, 160, 200, int(alpha/10)))  # type: ignore


    bk.alpha_composite(core_glow)
    bk = bk.filter(ImageFilter.GaussianBlur(radius=size//100))

    return Result(start_time, bk)