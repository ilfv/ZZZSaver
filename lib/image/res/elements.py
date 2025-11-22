from PIL import Image

from ..utils import open_rgba


class Attributes:
    phisical = open_rgba("res/elements/200.png")
    fire = open_rgba("res/elements/201.png")
    frost = open_rgba("res/elements/202.png")
    electric = open_rgba('res/elements/203.png')
    ether = open_rgba("res/elements/205.png")
    auric_inc = open_rgba("res/elements/206.png")

    alias_si = {
        "phisical": 200,
        "fire": 201,
        "frost": 202,
        "electric": 203,
        "ether": 205,
        "auric_inc": 206
    }

    alias_is = {
        200: "phisical",
        201: "fire",
        202: "frost",
        203: "electric",
        205: "ether",
        206: "auric_inc"
    }

    alias_io = {
        200: phisical,
        201: fire,
        202: frost,
        203: electric,
        205: ether,
        206: auric_inc
    }

    aid2el = {
        1371: 206       #Yixuan
    }

    @classmethod
    def get(cls, attribute: int) -> Image.Image:
        return cls.alias_io[attribute]

    @classmethod
    def get_by_id(cls, avatar_id: int, attribute: int) -> Image.Image:
        return cls.alias_io[cls.aid2el.get(avatar_id, attribute)]

class Professions:
    attack = open_rgba("res/elements/prof1.png")
    stun = open_rgba("res/elements/prof2.png")
    anomaly = open_rgba("res/elements/prof3.png")
    support = open_rgba("res/elements/prof4.png")
    defense = open_rgba("res/elements/prof5.png")
    rupture = open_rgba("res/elements/prof6.png")

    proff_list = [attack, stun, anomaly, support, defense, rupture]

    @classmethod
    def get(cls, proff: int) -> Image.Image:
        return cls.proff_list[proff - 1]
