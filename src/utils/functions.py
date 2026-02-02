import math
import random
from src.utils.settings import GalaxyType

def lerp_color(c1: tuple, c2: tuple, t) -> tuple[int, ...]:
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def get_random_coordinate_on_spiral(galaxy_config: GalaxyType, arm_count: int, arm_index, radius: float, scale: float, center: int, fragmentation: float=0.0, drift: float=0.0) -> tuple[int, int]:
    theta = (1.0 / galaxy_config.tightness) * math.log(radius + 0.1)
    theta += random.gauss(0, fragmentation/10) + drift/360
    theta += (arm_index * 2 * math.pi / arm_count)

    px = int(center + (radius * math.cos(theta) * scale))
    py = int(center + (radius * math.sin(theta) * scale))
    return px, py
