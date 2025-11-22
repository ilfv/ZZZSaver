from ..utils import open_rgba


class Grades:
    s_rank = open_rgba("res/grades/s_rank.png")
    a_rank = open_rgba("res/grades/a_rank.png")
    s_grade = open_rgba("res/grades/s_grade.png")
    a_grade = open_rgba("res/grades/a_grade.png")
    b_grade = open_rgba("res/grades/b_grade.png")

 
class Stars:
    light_star = open_rgba("res/stars/star_light.png")
    dark_star = open_rgba("res/stars/star_dark.png")


class ResStars:
    light_star = Stars.light_star.resize((24, 24))
    dark_star = Stars.dark_star.resize((24, 24))