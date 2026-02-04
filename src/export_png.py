import time
from PIL import Image
from src.utils.settings import Settings
from src.utils.result_obj import Result

def export_as_png(settings: Settings, size: int, background: Result, arm_1: Result, arm_2: Result, arm_3: Result, arm_4: Result, arm_5: Result, nebula: Result, hyperlane: Result, stars: Result, dust: Result) -> Result:
    if not settings.export.png:
        return Result(None, Image.new("RGBA", (1, 1), (0, 0, 0, 0)))

    comp_time = time.time()
    img = background.image

    if settings.steps.spirals:
        img.alpha_composite(arm_1.image, (0, 0))
        img.alpha_composite(arm_2.image, (0, 0))
        img.alpha_composite(arm_3.image, (0, 0))
        img.alpha_composite(arm_4.image, (0, 0))
        img.alpha_composite(arm_5.image, (0, 0))
    if settings.steps.nebula:
        img.alpha_composite(nebula.image, (0, 0))
    if settings.steps.hyperlanes and settings.steps.stars:
        img.alpha_composite(hyperlane.image, (0, 0))
    if settings.steps.stars:
        img.alpha_composite(stars.image, (0, 0))

    if settings.steps.dust:
        dust_layer = Image.new("RGBA", (size, size), (15, 10, 5, 255))
        img.paste(dust_layer, (0, 0), mask=dust.image)

    img.save("galaxy.png", "PNG")
    img.show()
    return Result(comp_time, Image.new("RGBA", (1, 1), (0, 0, 0, 0)))