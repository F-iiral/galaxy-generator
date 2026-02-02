import math
import random
import time
from PIL import Image, ImageDraw, ImageFilter
from src.utils.settings import Settings, GalaxyType
from src.utils.result_obj import Result

def generate_dust_lanes(settings: Settings, galaxy_config: GalaxyType, center: int, scale: float, size: int, arms: int) -> Result:
    start_time = time.time()
    dust_mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(dust_mask)

    amount_factor = settings.generation.dust.amount_factor

    dust_particles = int(amount_factor * size * size // (2000 * 2000))
    for _ in range(dust_particles):
        arm_index = random.randint(0, arms - 1)
        r = random.uniform(1.5, 12.0)
        theta_offset = -0.5
        theta = (1.0 / galaxy_config.tightness) * math.log(r + 0.1)
        theta += arm_index * 2 * math.pi / arms + theta_offset + random.gauss(0, 0.1)

        px = int(center + (r * math.cos(theta) * scale))
        py = int(center + (r * math.sin(theta) * scale))

        if 0 <= px < size and 0 <= py < size:
            rad = random.randint(1, 3) if random.random() > 0.2 else random.randint(4, 8)
            opacity = random.randint(20, 180)
            draw.ellipse([px-rad, py-rad, px+rad, py+rad], fill=opacity)

    dust_mask = dust_mask.filter(ImageFilter.BoxBlur(radius=size//100))
    return Result(start_time, dust_mask)