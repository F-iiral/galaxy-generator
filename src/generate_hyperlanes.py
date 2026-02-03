import random
import time
import numpy as np
from typing import Any
from scipy.spatial import KDTree
from PIL import Image, ImageDraw
from src.utils.settings import Settings, GalaxyType
from src.utils.result_obj import Result
from src.utils.functions import get_random_coordinate_on_spiral

cluster_chance = 0
branch_chance = 0
step_size = 0
hyperlane_max_length = 0

def draw_hyperlane(draw: ImageDraw.ImageDraw, origin: tuple[int, int], destination: tuple[int, int], tree: KDTree, star_array: np.ndarray[Any], hyperlane_condition):
    current_point = origin
    path = [origin]

    steps = 8
    dx = (destination[0] - origin[0]) / steps
    dy = (destination[1] - origin[1]) / steps

    for i in range(1, steps + 1):
        i_x = origin[0] + dx * i
        i_y = origin[1] + dy * i

        dist, index = tree.query([i_x, i_y])
        found_star = tuple(star_array[index])

        if dist <= hyperlane_max_length:
            draw.circle(found_star, 2, fill=(120, 180, 255, 150))
            if random.random() < hyperlane_condition:
                draw.line([current_point, found_star], fill=(120, 180, 255, 150), width=2)

            current_point = found_star
            path.append(found_star)

            # If we reached the actual destination star, we're done early
            if np.array_equal(found_star, destination):
                break
        else:
            # If a single link in the chain is too long, the path breaks
            break

def generate_side_cluster(draw: ImageDraw.ImageDraw, settings: Settings, galaxy_config: GalaxyType, tree: KDTree, star_array: np.ndarray[Any], origin: tuple[int, int]):
    global step_size

    cluster_size_factor = settings.generation.hyperlanes.cluster_size_factor
    cluster_size_alpha = settings.generation.hyperlanes.cluster_size_alpha
    cluster_size_beta = settings.generation.hyperlanes.cluster_size_beta

    cluster_size = int(random.betavariate(cluster_size_alpha, cluster_size_beta) * cluster_size_factor)
    nearby_stars = tree.query_ball_point(origin, r=hyperlane_max_length)
    random.shuffle(nearby_stars)

    for star in nearby_stars[:cluster_size]:
        c_star = tuple(star_array[star])

        if c_star != origin:
            draw_hyperlane(draw, origin, c_star, tree, star_array, 1)

def generate_side_hyperlane(draw: ImageDraw.ImageDraw, settings: Settings, galaxy_config: GalaxyType, tree: KDTree, star_array: np.ndarray[Any], origin: tuple[int, int], main_drift: float, arms: int, arm_index: int, scale: float, center: int, branch_r: float):
    global step_size

    branch_length_factor = settings.generation.hyperlanes.branch_length_factor
    branch_length_alpha = settings.generation.hyperlanes.branch_length_alpha
    branch_length_beta = settings.generation.hyperlanes.branch_length_beta
    branch_drift_mu = settings.generation.hyperlanes.branch_drift_mu
    branch_drift_sigma = settings.generation.hyperlanes.branch_drift_sigma

    branch_length = int(random.betavariate(branch_length_alpha, branch_length_beta) * branch_length_factor)
    branch_drift = random.normalvariate(branch_drift_mu, branch_drift_sigma) + main_drift
    branch_path = [origin]

    fragmentation = settings.generation.fragmentation.small_hyperlanes

    break_chance_min = settings.generation.hyperlanes.break_chance_max
    break_chance_min = settings.generation.hyperlanes.break_chance_min
    hyperlane_condition = 1- random.uniform(break_chance_min, break_chance_min)

    for _ in range(branch_length):
        branch_r += step_size
        bx, by = get_random_coordinate_on_spiral(galaxy_config, arms, arm_index, branch_r, scale, center, fragmentation=fragmentation, drift=branch_drift)
        b_dist, b_index = tree.query([bx, by])

        if b_dist < hyperlane_max_length:
            b_star = tuple(star_array[b_index])
            if b_star != branch_path[-1]:
                draw_hyperlane(draw, branch_path[-1], b_star, tree, star_array, hyperlane_condition)
                branch_path.append(b_star)


def generate_main_hyperlane(draw: ImageDraw.ImageDraw, settings: Settings, galaxy_config: GalaxyType, tree: KDTree, star_array: np.ndarray[Any], arms: int, arm_index: int, scale: float, center: int):
    global cluster_chance, branch_chance, step_size

    current_r = galaxy_config.bar + 0.5 # Start just outside the core
    last_special_generation = 0

    fragmentation = settings.generation.fragmentation.hyperlanes

    main_length_factor = settings.generation.hyperlanes.main_length_factor
    main_length_alpha = settings.generation.hyperlanes.main_length_alpha
    main_length_beta = settings.generation.hyperlanes.main_length_beta
    main_drift = settings.generation.hyperlanes.main_drift
    break_chance_min = settings.generation.hyperlanes.break_chance_max
    break_chance_min = settings.generation.hyperlanes.break_chance_min
    special_generation_distance = settings.generation.hyperlanes.special_generation_distance

    main_drift = random.uniform(-main_drift, main_drift)
    hyperlane_condition = 1 - random.uniform(break_chance_min, break_chance_min)
    path_stars = []

    max_r = int(random.betavariate(main_length_alpha, main_length_beta) * main_length_factor)
    while current_r < max_r:
        ix, iy = get_random_coordinate_on_spiral(galaxy_config, arms, arm_index, current_r, scale, center, fragmentation=fragmentation, drift=main_drift)
        dist, index = tree.query([ix, iy])
        current_r += step_size

        if dist < hyperlane_max_length:
            star_pos = tuple(star_array[index])
            if not path_stars or star_pos != path_stars[-1]:
                path_stars.append(star_pos)

    for i in range(len(path_stars) - 1):
        m_star_1 = path_stars[i]
        m_star_2 = path_stars[i+1]

        draw_hyperlane(draw, m_star_1, m_star_2, tree, star_array, hyperlane_condition)

        if random.random() < branch_chance and last_special_generation <= special_generation_distance:
            last_special_generation = special_generation_distance
            generate_side_hyperlane(
                draw=draw,
                settings=settings,
                galaxy_config=galaxy_config,
                tree=tree,
                star_array=star_array,
                origin=m_star_1,
                main_drift=main_drift,
                arms=arms,
                arm_index=arm_index,
                scale=scale,
                center=center,
                branch_r=galaxy_config.bar + 0.5 + (i * step_size)
            )
        elif random.random() < cluster_chance and last_special_generation <= special_generation_distance:
            last_special_generation = special_generation_distance
            generate_side_cluster(
                draw=draw,
                settings=settings,
                galaxy_config=galaxy_config,
                tree=tree,
                star_array=star_array,
                origin=m_star_1
            )
        else:
            last_special_generation -= 1


def generate_hyperlanes(settings: Settings, galaxy_config: GalaxyType, center: int, scale: float, size: int, arms: int, star_coords: set[tuple[int, int]]) -> Result:
    global step_size, branch_chance, cluster_chance, hyperlane_max_length, hyperlane_max_length_sqr
    start_time = time.time()
    lane_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(lane_img)

    star_array = np.array(list(star_coords))
    tree = KDTree(star_array)

    step_size = settings.generation.hyperlanes.step_size
    cluster_chance = settings.generation.hyperlanes.cluster_chance
    branch_chance = settings.generation.hyperlanes.branch_chance
    hyperlane_max_length = size / settings.generation.hyperlanes.hyperlane_max_length_factor

    for arm_index in range(arms):
        generate_main_hyperlane(draw, settings, galaxy_config, tree, star_array, arms, arm_index, scale, center)

    return Result(start_time, lane_img)
