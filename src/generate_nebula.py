import random
import time
from PIL import Image, ImageDraw, ImageFilter
from src.utils.result_obj import Result
from src.utils.functions import get_random_coordinate_on_spiral
from src.utils.settings import Settings, GalaxyType

def generate_nebula(settings: Settings, galaxy_config: GalaxyType, center: int, scale: float, size: int, arms: int) -> Result:
    if not settings.steps.nebula:
        return Result(None, Image.new("RGBA", (1, 1), (0, 0, 0, 0)))

    start_time = time.time()
    h2_regions = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(h2_regions)

    gas_color = (255, 100, 150)
    bright_color = (255, 200, 230)

    fragmentation = settings.generation.fragmentation.nebula
    band_spacing = settings.generation.nebula.band_spacing
    band_thickness = settings.generation.nebula.band_thickness
    amount_factor = settings.generation.nebula.amount_factor

    num_clumps = int(amount_factor * arms * size * size // (2000 * 2000))
    for _ in range(num_clumps):
        arm_index = random.randint(0, arms - 1)
        ring_index = random.sample([1, 1, 1, 1, 2, 2, 3], 1)[0]
        r = (ring_index * band_spacing) + random.uniform(-band_thickness, band_thickness)

        px, py = get_random_coordinate_on_spiral(galaxy_config, arms, arm_index, r, scale, center, fragmentation=fragmentation)

        for _ in range(random.randint(3, 8)):
            offset_x = random.gauss(0, size // 200)
            offset_y = random.gauss(0, size // 200)

            rad = random.randint(size // 300, size // 150)
            opacity = random.randint(40, 100)

            draw.ellipse(
                [px + offset_x - rad, py + offset_y - rad,
                 px + offset_x + rad, py + offset_y + rad],
                fill=(*bright_color, opacity)
            )
            draw.ellipse(
                [px + offset_x * 0.1 - rad, py + offset_y * 0.1 - rad,
                 px + offset_x * 0.1 + rad, py + offset_y * 0.1 + rad],
                fill=(*gas_color, opacity)
            )

    h2_regions = h2_regions.filter(ImageFilter.GaussianBlur(radius=size // 150))
    return Result(start_time, h2_regions)
