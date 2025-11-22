from ..utils import open_rgba


class Backgrounds:
    dark_bg = open_rgba("res/deadly_assault/dark_bg.png").crop((0, 0, 3840, 1180))
    det_card_bg = open_rgba("res/deadly_assault/det_card_bg.png")
    buddy_bg = open_rgba("res/buddy_bg.png")
    main_info_bg = open_rgba("res/deadly_assault/main_info_bg.png").crop((0, 0, 1448, 300))
    empty_img = open_rgba("res/empty_img.png")
    

class ResBackgrounds:
    dark_bg = Backgrounds.dark_bg.resize((1448, 1180))
    det_card_bg = Backgrounds.det_card_bg.resize((900, 150))
    buddy_bg = Backgrounds.buddy_bg.resize((240, 240))
    main_info_bg = Backgrounds.main_info_bg
    empty_img = Backgrounds.empty_img.resize((480, 480))
