from PIL import Image


class Grades:
    s = Image.open("res/s_grade.png").resize((18, 18))
    a = Image.open("res/a_grade.png").resize((18, 18))

class Stars:
    light_star = Image.open("res/star_light.png").resize((20, 20))
    dark_star = Image.open("res/star_dark.png").resize((20, 20))

class Others:
    dark_bg = Image.open("res/dark_bg.png")
    det_card_bg = Image.open("res/det_card_bg.png")
    waiting = Image.open("res/wait_img.png")
