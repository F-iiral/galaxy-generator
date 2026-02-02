import math
import random
import time
from PIL import Image, ImageDraw
from src.utils.functions import get_random_coordinate_on_spiral, lerp_color
from src.utils.result_obj import Result
from src.utils.settings import Settings, GalaxyType

def has_collision(x, y, occupied_pixels, radius=3) -> bool:
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if (x + dx, y + dy) in occupied_pixels:
                return True
    return False

def draw_star(draw, px, py, color, shape) -> None:
    brightness = random.uniform(0.8, 1.5)
    base_color = tuple(min(255, int(c * brightness)) for c in color)

    glow_radius = random.randint(2, 3)
    for r in range(glow_radius, 0, -1):
        alpha = int(20 * (1.0 - (r / (glow_radius + 1))))
        glow_color = base_color + (alpha,)
        draw.ellipse([px-r, py-r, px+r, py+r], fill=glow_color)

    glow_faint = base_color + (60,)
    match shape:
        case "cross" | "big_cross":
            length = 1 if shape == "cross" else 2
            draw.line([(px-length, py), (px+length, py)], fill=glow_faint, width=1)
            draw.line([(px, py-length), (px, py+length)], fill=glow_faint, width=1)
        case "x" | "big_x":
            length = 1 if shape == "x" else 2
            draw.line([(px-length, py-length), (px+length, py+length)], fill=glow_faint, width=1)
            draw.line([(px+length, py-length), (px-length, py+length)], fill=glow_faint, width=1)

    core_color = lerp_color(base_color, (255, 255, 255), 0.7)
    draw.point((px, py), fill=core_color)

def generate_stars(settings: Settings, galaxy_config: GalaxyType, center: int, scale: float, size: int, arms: int, num_stars: int) -> Result:
    start_time = time.time()
    stars = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    star_draw = ImageDraw.Draw(stars, "RGBA")

    border_inner = size // 20
    border_outer = size - size // 20

    star_coords = set()
    occupied_pixels = set()
    star_colors = [
        (157, 180, 255), # O5(V)
        (162, 185, 255), # B1(V)
        (167, 188, 255), # B3(V)
        (170, 191, 255), # B5(V)
        (175, 195, 255), # B8(V)
        (186, 204, 255), # Al(V)
        (192, 209, 255), # A3(V)
        (202, 216, 255), # A5(V)
        (228, 232, 255), # FO(V)
        (237, 238, 255), # F2(V)
        (251, 248, 255), # F5(V)
        (255, 249, 249), # F8(V)
        (255, 245, 236), # G2(V)
        (255, 244, 232), # G5(V)
        (255, 241, 223), # G8(V)
        (255, 235, 209), # KO(V)
        (255, 215, 174), # K4(V)
        (255, 198, 144), # K7(V)
        (255, 190, 127), # M2(V)
        (255, 187, 123), # M4(V)
        (255, 187, 123), # M6(V)
    ]
    star_shapes = [
        ("dot", 0),
        ("cross", 2),
        ("big_cross", 2),
        ("x", 2),
        ("big_x", 3),
    ]

    fragmentation = settings.generation.fragmentation.stars

    for _ in range(num_stars):
        spiral_chance = 1 - galaxy_config.core_chance

        if random.random() < spiral_chance:
            arm_index = random.randint(0, arms - 1)
            r = random.expovariate(0.6) + galaxy_config.bar + 0.2
            px, py = get_random_coordinate_on_spiral(galaxy_config, arms, arm_index, r, scale, center, fragmentation=fragmentation)
        else:
            r_x = random.uniform(0, galaxy_config.core_spread * (1 + galaxy_config.bar * 0.5))
            r_y = random.uniform(0, galaxy_config.core_spread * (1 + galaxy_config.bar * 0.5))
            angle_core = random.uniform(0, 2 * math.pi)

            lx = r_x * math.cos(angle_core)
            ly = r_y * math.sin(angle_core)

            rotation = 80
            px = int(center + (lx * math.cos(rotation) - ly * math.sin(rotation)) * scale)
            py = int(center + (lx * math.sin(rotation) + ly * math.cos(rotation)) * scale)

        if not (border_inner <= px < border_outer and border_inner <= py < border_outer):
            continue

        dist_from_center = math.sqrt(px**2 + py**2)
        if dist_from_center < 0.6:      collision_buffer = 1
        elif dist_from_center < 1:      collision_buffer = 2
        elif dist_from_center < 1.25:   collision_buffer = 4 if random.random() > 0.3 else 3
        elif dist_from_center < 1.5:    collision_buffer = 4 if random.random() > 0.5 else 5
        elif dist_from_center < 1.75:   collision_buffer = 5 if random.random() > 0.7 else 4
        else:                           collision_buffer = 4

        star_color = random.choice(star_colors)
        shape, shape_radius = random.choice(star_shapes)

        if has_collision(px, py, occupied_pixels, radius=collision_buffer + shape_radius):
            continue

        draw_star(star_draw, px, py, star_color, shape)
        occupied_pixels.add((px, py))
        star_coords.add((px, py))

    return Result(start_time, stars, star_coords)