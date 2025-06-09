from PIL import Image, ImageDraw


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
