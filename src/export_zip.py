import io
import zipfile
import time
from PIL import Image
from src.utils.settings import Settings
from src.utils.result_obj import Result

def export_as_zip(settings: Settings, size: int, background: Result, arm_1: Result, arm_2: Result, arm_3: Result, arm_4: Result, arm_5: Result, nebula: Result, hyperlane: Result, stars: Result, dust: Result) -> Result:
    if not settings.export.zip:
        return Result(None, Image.new("RGBA", (1, 1), (0, 0, 0, 0)))

    comp_time = time.time()
    layers_to_export = {}

    if settings.steps.spirals:
        # Adding arms individually or as a group
        for i, arm in enumerate([arm_1, arm_2, arm_3, arm_4, arm_5], 1):
            layers_to_export[f"01_arm_{i}.png"] = arm.image

    if settings.steps.nebula:
        layers_to_export["02_h2_nebula.png"] = nebula.image

    if settings.steps.hyperlanes and settings.steps.stars:
        layers_to_export["03_hyperlanes.png"] = hyperlane.image

    if settings.steps.stars:
        layers_to_export["04_stars.png"] = stars.image

    if settings.steps.dust:
        dust_layer = Image.new("RGBA", (size, size), (15, 10, 5, 255))
        exported_dust = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        exported_dust.paste(dust_layer, (0, 0), mask=dust.image)
        layers_to_export["05_dust.png"] = exported_dust

    with zipfile.ZipFile("galaxy_layers.zip", "w") as zf:
        img_byte_arr = io.BytesIO()
        background.image.save(img_byte_arr, format='PNG')
        zf.writestr("00_background.png", img_byte_arr.getvalue(), compresslevel=3)

        # Loop through the generated layers
        for filename, layer_img in layers_to_export.items():
            img_byte_arr = io.BytesIO()
            layer_img.save(img_byte_arr, format='PNG')
            zf.writestr(filename, img_byte_arr.getvalue())
    return Result(comp_time, Image.new("RGBA", (1, 1), (0, 0, 0, 0)))