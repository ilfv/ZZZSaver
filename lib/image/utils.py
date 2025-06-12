import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

_pattern = re.compile(r"<color=(#\w{6})>(.*?)</color>")


def round_corners(img: Image.Image, radius: int):
    width, height = img.size
    alpha = Image.new('L', img.size, 255)
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)

    draw.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)

    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, height - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (width - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (width - radius, height - radius))

    img.putalpha(alpha)

    return img

def fade_alpha(image: Image.Image)  -> Image.Image:
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    arr = np.array(image)
    height, width = arr.shape[:2]

    alpha_mask = np.linspace(0, 255, width, dtype=np.uint8)
    alpha_mask = np.tile(alpha_mask, (height, 1))

    arr[:, :, 3] = alpha_mask

    return Image.fromarray(arr, mode='RGBA')
