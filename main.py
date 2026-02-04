import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from PIL import Image
from src.export_zip import export_as_zip
from src.export_png import export_as_png
from src.generate_background import generate_background
from src.generate_dust import generate_dust_lanes
from src.generate_hyperlanes import generate_hyperlanes
from src.generate_nebula import generate_nebula
from src.generate_spirals import generate_spiral_arms
from src.generate_stars import generate_stars
from src.utils.settings import Settings
from src.utils.result_obj import Result
import hjson
import os

def load_settings(config_path:str='settings.hjson') -> Settings:
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                raw_data = hjson.load(f)
            settings = Settings(**raw_data)
            return settings
        except (hjson.HjsonDecodeError, IOError):
            print(f"Warning: Could not parse {config_path}. Using defaults.")
        return Settings(**{})
    else:
        return Settings(**{})

def generate_galaxy(settings: Settings, size:int, galaxy_type:str, arms:int, num_stars:int) -> None:
    start_time = time.time()
    center = size // 2
    scale = size / 20
    galaxy_config = settings.galaxy_types.get(galaxy_type, None)
    if galaxy_config == None:
        print(f"Invalid Galaxy Type: '{galaxy_type}'!")
        time.sleep(10)
        exit()
    if arms <= 2:
        print("The Galaxy must have atleast 3 arms!")
        time.sleep(10)
        exit()

    print("Working...")
    with ProcessPoolExecutor() as executor:
        bk_future = executor.submit(generate_background, settings, size, center)
        stars_future = executor.submit(generate_stars, settings, galaxy_config, center, scale, size, arms, num_stars)
        arm_1_future = executor.submit(generate_spiral_arms, settings, galaxy_config, center, scale*0.5, size, arms, [(0, 0, 0, 0), (87, 161, 191, 50), (30, 65, 79)], 0.1)
        arm_2_future = executor.submit(generate_spiral_arms, settings, galaxy_config, center, scale, size, arms, [(0, 0, 0, 0), (87, 161, 191, 50), (30, 65, 79)], 0.1)
        arm_3_future = executor.submit(generate_spiral_arms, settings, galaxy_config, center, scale*1, size, arms, [(255, 240, 200), (100, 50, 200), (20, 30, 60)], 0.15)
        arm_4_future = executor.submit(generate_spiral_arms, settings, galaxy_config, center, scale*2, size, arms, [(255, 240, 200), (50, 60, 250), (10, 10, 90)], 0.15)
        arm_5_future = executor.submit(generate_spiral_arms, settings, galaxy_config, center, scale*2, size, arms, [(0, 0, 0), (71, 42, 6), (0, 0, 0)], 0.05)
        dust_nebula_future = executor.submit(generate_dust_lanes, settings, galaxy_config, center, scale, size, arms)
        h2_nebula_future = executor.submit(generate_nebula, settings, galaxy_config, center, scale, size, arms)

        background = bk_future.result()
        stars = stars_future.result()
        arm_1 = arm_1_future.result()
        arm_2 = arm_2_future.result()
        arm_3 = arm_3_future.result()
        arm_4 = arm_4_future.result()
        arm_5 = arm_5_future.result()
        dust_nebula = dust_nebula_future.result()
        h2_nebula = h2_nebula_future.result()

    hyperlane_result = generate_hyperlanes(settings, galaxy_config, center, scale, size, arms, stars.data[0])

    print("Exporting...")
    with ProcessPoolExecutor() as executor:
        png_future = executor.submit(export_as_png, settings, size, background, arm_1, arm_2, arm_3, arm_4, arm_5, h2_nebula, hyperlane_result, stars, dust_nebula)
        zip_future = executor.submit(export_as_zip, settings, size, background, arm_1, arm_2, arm_3, arm_4, arm_5, h2_nebula, hyperlane_result, stars, dust_nebula)

        png = png_future.result()
        zip = zip_future.result()

    print(f"Saved {size}x{size} PNG as galaxy.png")
    print(f"Total stars placed: {stars.data[0].__len__() if stars.data else "NaN"}/{num_stars}")
    print(f"""Generation took a total of {round(time.time() - start_time, 2)}s
- Composition (PNG): {round(png.time, 2).__str__() + "s" if png.time else "[skipped]"}
- Composition (ZIP): {round(zip.time, 2).__str__() + "s" if zip.time else "[skipped]"}
- Background: {round(background.time, 2).__str__() + "s" if background.time else "[skipped]"}
- Spiral Arm Pass 1: {round(arm_1.time, 2).__str__() + "s" if arm_1.time else "[skipped]"}
- Spiral Arm Pass 2: {round(arm_2.time, 2).__str__() + "s" if arm_2.time else "[skipped]"}
- Spiral Arm Pass 3: {round(arm_3.time, 2).__str__() + "s" if arm_3.time else "[skipped]"}
- Spiral Arm Pass 4: {round(arm_4.time, 2).__str__() + "s" if arm_4.time else "[skipped]"}
- Spiral Arm Pass 5: {round(arm_5.time, 2).__str__() + "s" if arm_5.time else "[skipped]"}
- Hydrogen Nebula: {round(h2_nebula.time, 2).__str__() + "s" if h2_nebula.time else "[skipped]"}
- Dust Nebula: {round(dust_nebula.time, 2).__str__() + "s" if dust_nebula.time else "[skipped]"}
- Hyperlanes: {round(hyperlane_result.time, 2).__str__() + "s" if hyperlane_result.time else "[skipped]"}
- Stars: {round(stars.time, 2).__str__() + "s" if stars.time else "[skipped]"}""")

    print("This window will close in 10 seconds.")
    time.sleep(10)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    settings = load_settings()

    if settings.manual:
        size = int(input("> Size of image in pixel? "))
        arms = int(input("> Amount of spiral arms? "))
        stars = int(input("> Amount of star spawns? "))
        type = str(input("> Galaxy Type? "))
    else:
        size = settings.parameters.size
        arms = settings.parameters.arms
        stars = settings.parameters.stars
        type = settings.parameters.type

    generate_galaxy(settings, size, type, arms, stars)