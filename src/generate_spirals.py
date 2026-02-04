import math
import random
import time
from PIL import Image, ImageDraw, ImageFilter
from src.utils.result_obj import Result
from src.utils.functions import get_random_coordinate_on_spiral, lerp_color
from src.utils.settings import Settings, GalaxyType

def generate_spiral_arms(settings: Settings, galaxy_config: GalaxyType, center: int, scale: float, size: int, arms: int, colors, weakness) -> Result:
    if not settings.steps.spirals:
        return Result(None, Image.new("RGBA", (1, 1), (0, 0, 0, 0)))

    start_time = time.time()
    nebula = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    neb_draw = ImageDraw.Draw(nebula)

    core_color = colors[0]
    mid_color = colors[1]
    outer_color = colors[2]
    fragmentation = settings.generation.fragmentation.spirals
    amount_factor = settings.generation.spirals.amount_factor

    nebula_count = int(amount_factor * size * size // (2000 * 2000))
    for _ in range(nebula_count):
        arm_index = random.randint(0, arms - 1)
        r = random.uniform(0.1, 15.0)

        norm_r = min(r / 15.0, 1.0)

        if norm_r < 0.4:
            current_color = lerp_color(core_color, mid_color, norm_r / 0.4)
        else:
            current_color = lerp_color(mid_color, outer_color, (norm_r - 0.4) / 0.7)

        # Fade opacity exponentially as it gets further out
        opacity = int(255 * math.exp(-0.2 * r) * weakness)
        fill_tuple = current_color + (opacity,)

        px, py = get_random_coordinate_on_spiral(galaxy_config, arms, arm_index, r, scale, center, fragmentation=fragmentation)

        if 0 <= px < size and 0 <= py < size:
            rad = int((size - size * r * 0.06) // 60)
            neb_draw.ellipse([px-rad, py-rad, px+rad, py+rad], fill=fill_tuple)

    nebula = nebula.filter(ImageFilter.GaussianBlur(radius=size//70))
    return Result(start_time, nebula)