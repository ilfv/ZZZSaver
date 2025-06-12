from PIL import Image


class Grades:
    s = Image.open("res/s_grade.png")
    a = Image.open("res/a_grade.png")


class Stars:
    light_star = Image.open("res/star_light.png")
    dark_star = Image.open("res/star_dark.png")


class Backgrounds:
    dark_bg = Image.open("res/dark_bg.png").crop((0, 0, 3840, 1180)).convert("RGBA")
    det_card_bg = Image.open("res/det_card_bg.png").convert("RGBA")
    buddy_bg = Image.open("res/buddy_bg.png").convert("RGBA")
    main_info_bg = Image.open("res/main_info_bg.png").crop((0, 0, 1448, 300)).convert("RGBA")


class TgResStars:
    light_star = Stars.light_star.resize((24, 24))
    dark_star = Stars.dark_star.resize((24, 24))
    

class TgResBackgrounds:
    dark_bg = Backgrounds.dark_bg.resize((1448, 1180))
    det_card_bg = Backgrounds.det_card_bg.resize((900, 150))
    buddy_bg = Backgrounds.buddy_bg.resize((240, 240))
    main_info_bg = Backgrounds.main_info_bg


class GRGrades:
    s = Grades.s.resize((18, 18))
    a = Grades.a.resize((18, 18))

class GRStars:
    light_star = Stars.light_star.resize((20, 20))
    dark_star = Stars.dark_star.resize((20, 20))

class GRBackgrounds:
    dark_bg = Backgrounds.dark_bg.resize((400, 100))
    det_card_bg = Backgrounds.det_card_bg.resize((600, 150))
    buddy_bg = Backgrounds.buddy_bg.resize((240, 240))
