from string import whitespace
from typing import TYPE_CHECKING
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from lib.image.base import BaseGen
from lib.image.res.others import Grades
from lib.image.res.shiyu_defense import Backgrounds, Others
from lib.image.res.elements import Attributes
from lib.image.utils import linear_gradient, round_corners, fade_alpha
from lib.utils import singleton

if TYPE_CHECKING:
    from lib.data_classes.api import (ShiyuDefenseStruct, SDImagesStruct, SDFloorDetailStruct, 
                                      SDMonsterInfoStruct, SDMonsterStruct, SDImgMonsterStruct)


class Sizes:
    main_bg = (978, 1524)
    main_info = (910, 180)
    challenge = (910, 295)
    challenge_avatar = (100, 125)
    challenge_buddy = (80, 105)
    monsters_info = (600, 550)


class Fonts:
    class MainInfo:
        time = ImageFont.truetype("arial.ttf", 15)
        text = ImageFont.truetype('res/fonts/inpin.ttf', 15)
        nums = ImageFont.truetype('res/fonts/inpin.ttf', 15)

    class Challenge:
        main_label = ImageFont.truetype("res/fonts/inpin.ttf", 15)
        sub_main_label = ImageFont.truetype("res/fonts/DejaVuSans.ttf", 13)
        inner_label = ImageFont.truetype("arial.ttf", 10)
        enemy_info_label = ImageFont.truetype("res/fonts/DejaVuSans.ttf", 10)

        battle_time = ImageFont.truetype("arial.ttf", 15)
        challenge_time = ImageFont.truetype("res/fonts/inpin.ttf", 13)


@singleton
class GenerateBg:
    text = {"main_info": {"main_label": ("Обзор испытания", None, 45),    #label: (text, text_color, font_size)
                          "highest_line": ("Наивысшая пройденная линия обороны:", (100, 100, 100), 25)},
            "challenge": {"inner": ("Время прохождения", (90, 90, 90), 20)}}
    colors = {"main_info": {"top": (10, 10, 10), "bottom": (22, 24, 23), "inner": ((15, 16, 16), (24, 26, 25))},
              "challenge": {"top": (10, 10, 10), "bottom": (29, 31, 30), "inner": (22, 24, 23), "line": (40, 40, 40)}}

    @lru_cache(None)
    def main_info(self, paste_icons: bool = True, paste_text: bool = True, 
                  round_corner_rad: int = 25, inner_round_corners: int = 15, 
                  title_font: str = "res/fonts/inpin.ttf",
                  sym_font: str = "res/fonts/DejaVuSans.ttf", default_font: str = "arial.ttf") -> Image.Image:
        bg = Backgrounds.main_info.copy()
        img = Image.new("RGBA", (bg.size[0], int(bg.size[1] / 75 * 100)), self.colors["main_info"]["bottom"])
        inner = linear_gradient((int(img.size[0] * 0.94), int(img.size[1] * 0.42)), 
                                self.colors["main_info"]["inner"][0],
                                self.colors["main_info"]["inner"][1]).convert("RGBA")
        
        if inner_round_corners:
            inner = round_corners(inner, inner_round_corners)

        img.paste(bg, (0, img.size[1] - bg.size[1]) + img.size, bg)
        sx, sy = int(img.size[0] * 0.033), int(img.size[1] * 0.36)
        img.paste(inner, (sx, sy, inner.size[0] + sx, inner.size[1] + sy), inner)

        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, img.size[0], img.size[1] - bg.size[1]), self.colors["main_info"]["top"])

        img = round_corners(img, round_corner_rad)
            
        draw = ImageDraw.Draw(img)

        if paste_icons:
            grade_size = inner.size[1] - inner.size[1] // 5
            x = int(sx + inner.size[0] / 10)
            y = int(sy + inner.size[1] / 10)
            step = inner.size[0] // 3
            
            for ind, grade in enumerate(grd.resize((grade_size,) * 2) for grd in [Grades.s_grade, Grades.a_grade, Grades.b_grade]):
                img.paste(grade, (x + step * ind, y, x + grade.size[0] + step * ind, y + grade.size[1]), grade)
                draw.text((x + step * ind + grade.size[0] + grade.size[0] // 5, y + grade.size[1] // 3.3), 
                          u"\u00d7", fill=(0x49, 0x4d, 0x4e), font=ImageFont.truetype(sym_font, 36))
                
        if paste_text:
            text = self.text["main_info"]
            main_label, highest_line = text["main_label"], text["highest_line"]

            draw.text((int(img.size[0] * 0.02), int(img.size[1] * 0.05)), main_label[0], fill=main_label[1],
                      font=ImageFont.truetype(title_font, main_label[2]))
            draw.text((int(img.size[0] * 0.02), img.size[1] - int(img.size[1] * 0.15)), highest_line[0],
                      fill=highest_line[1], font=ImageFont.truetype(default_font, highest_line[2]))

        return img
    
    @lru_cache(None)
    def challenge(self, size: tuple[int, int] = (1400, 448), round_corner_ang: int = 25, 
                  inner_round_corners: int = 15, default_font: str = "arial.ttf") -> Image.Image:
        bg = Image.new("RGBA", size, self.colors["challenge"]["bottom"])
        inner = Image.new("RGBA", (int(size[0] * 0.45), int(size[1] * 0.10)), self.colors["challenge"]["inner"])

        inner = round_corners(inner, inner_round_corners)
        text = self.text["challenge"]["inner"]
        draw = ImageDraw.Draw(inner)
        draw.text((int(inner.size[0] * 0.03), int(inner.size[1] * 0.19)), text[0], text[1], ImageFont.truetype(default_font, text[2]))
        
        x, y = int(size[0] * 0.03), int(size[1] * 0.83)
        line_x = size[0] // 2
        bg.paste(inner, (x, y, x + inner.size[0], y + inner.size[1]), inner)
        bg.paste(inner, (line_x + x, y, line_x + x + inner.size[0], y + inner.size[1]), inner)

        team_y = int(size[1] * 0.23)
        team_size = (int(size[0] * 0.07), int(size[1] * 0.06))
        team1, team2 = (img.resize(team_size) for img in (Others.team1, Others.team2))
        bg.paste(team1, (x, team_y, x + team_size[0], team_y + team_size[1]), team1)
        bg.paste(team2, (line_x + x, team_y, line_x + x + team_size[0], team_y + team_size[1]), team2)

        draw = ImageDraw.Draw(bg)
        draw.line((line_x, int(size[1] * 0.28), line_x, y + int(inner.size[1] * 0.1)), self.colors["challenge"]["line"], 2)
        draw.rectangle((0, 0, size[0], int(size[1] * 0.18)), fill=self.colors["challenge"]["top"])

        return round_corners(bg, round_corner_ang)
    
    @lru_cache(None)
    def monsters_info(self, size: tuple[int, int] = (600, 544), font: str = "arial.ttf", font_size: int = 20,
                      round_corners_ang: int = 15) -> Image.Image:
        img = Image.new("RGBA", size, (29, 31, 30))
        top = Image.new("RGBA", (size[0], int(size[1] * 0.08)), (10, 10, 10))
        ImageDraw.Draw(top).text((top.size[0] // 10, top.size[1] // 4), "Информация о противниках", font=ImageFont.truetype(font, font_size))
        img.paste(top, (0, 0) + top.size)
        return round_corners(img, round_corners_ang)


@singleton
class SDImageGen(BaseGen):
    _main_info_bg = None
    _challenge_bg = None
    _challenge_enemy_info_bg = None
    _monsters_bg = None

    colors = {"challenge": {
        "main_label": (255, 255, 255),
        "sub_main_label": (150, 150, 150),
        "floor_challenge_time": (90, 90, 90),
        "battle_time": (255, 255, 255),
        "inner_label": (115, 115, 115),
        "enemy_info": (0, 0, 0)
    }}

    def __init__(self, bg_gen = GenerateBg(), sizes = Sizes(), fonts = Fonts()):
        self.bg_gen = bg_gen
        self.sizes = sizes
        self.fonts = fonts

    @property
    def main_info_bg(self) -> Image.Image:
        if self._main_info_bg is None:
            self._main_info_bg = self.bg_gen.main_info().resize(self.sizes.main_info)
        
        return self._main_info_bg.copy()
    
    @property
    def challenge_bg(self) -> Image.Image:
        if self._challenge_bg is None:
            self._challenge_bg = self.bg_gen.challenge().resize(self.sizes.challenge)

        return self._challenge_bg.copy()
    
    @property
    def monsters_info_bg(self) -> Image.Image:
        if self._monsters_bg is None:
            self._monsters_bg = self.bg_gen.monsters_info().resize(self.sizes.monsters_info)

        return self._monsters_bg.copy()
    
    @property
    def challenge_enemy_info(self):
        if not self._challenge_enemy_info_bg:
            msx, msy = self.sizes.challenge
            img = Image.new("RGBA", (int(msx * 0.19), int(msy * 0.05)), (125, 126, 127, 255))
            ImageDraw.Draw(img).text((int(img.size[0] * 0.03), int(img.size[1] * 0.02)), u"Информация о противниках \u25ba",
                                     self.colors['challenge']["enemy_info"], self.fonts.Challenge.enemy_info_label)
            
            self._challenge_enemy_info_bg = round_corners(img, 8)
        
        return self._challenge_enemy_info_bg.copy()

    def generate(self, data: 'ShiyuDefenseStruct', icons: 'SDImagesStruct | None', challenge_enemy_info: bool = False) -> Image.Image:
        if not (data and data.has_data):
            return self.empty_img

        self.img = Backgrounds.main_bg.resize(self.sizes.main_bg)
        self.draw = ImageDraw.Draw(self.img)

        self.main_info(data)

        base_x = int(self.sizes.main_bg[0] * 0.03)
        ypad = int(self.sizes.main_bg[1] * 0.02)
        chx, chy = self.sizes.challenge
        y = self.sizes.main_info[1] + ypad

        for floor in data.all_floor_detail:
            challenge_img = self.challenge(floor, icons, challenge_enemy_info)
            y += ypad

            self.img.paste(challenge_img, (base_x, y, base_x + chx, y + chy), challenge_img)
            y += chy

        return self.img

    def main_info(self, data: 'ShiyuDefenseStruct', xy: tuple[int, int] = (32, 32)) -> None:
        img = self.main_info_st(data)
        self.img.paste(img, xy + tuple(xy[i] + img.size[i] for i in range(2)), img)
    
    @staticmethod
    def main_info_st(data: 'ShiyuDefenseStruct', paste_time: bool = True, bg: Image.Image | None = None, 
                     time_color: tuple[int, int, int] = (100, 100, 100),
                     text_color: tuple[int, int, int] = (255, 255, 255),
                     bg_gen = GenerateBg(), sizes = Sizes(), fonts = Fonts()) -> Image.Image:
        if bg is None:
            bg = bg_gen.main_info().resize(sizes.main_info)
        else:
            bg = bg.resize(sizes.main_info)
        draw = ImageDraw.Draw(bg)
        fonts = fonts.MainInfo
        
        ratings = {rating.rating: rating.times for rating in data.rating_list}
        ratings = [ratings.get(rrar, 0) for rrar in "SAB"]
        x, y, step = int(bg.size[0] * 0.25), int(bg.size[1] * 0.5), int(bg.size[0] * 0.312) 
        for i in range(3):
            draw.text((x + step * i, y), str(ratings[i]), text_color, fonts.nums)

        if data.has_data:
            draw.text((int(bg.size[0] * 0.3), int(bg.size[1] * 0.83)), data.all_floor_detail[0].zone_name,
                      text_color, fonts.text)
        
        if paste_time and data.has_data:
            draw.text((int(bg.size[0] * 0.67), int(bg.size[1] * 0.08)), f"Период посчёта: {data.hadal_begin_time.strftime('%d.%m.%Y')} - "
                      f"{data.hadal_end_time.strftime('%d.%m.%Y')}", time_color, fonts.time)

        return bg

    def challenge(self, data: 'SDFloorDetailStruct', icons: 'SDImagesStruct', paste_enemy_info: bool = True) -> Image.Image:
        colors = self.colors["challenge"]
        fonts = self.fonts.Challenge
        bg = self.challenge_bg
        draw = ImageDraw.Draw(bg)
        msx, msy = bg.size
        base_x = int(msx * 0.03)

        #Top
        draw.text((base_x, int(msy * 0.03)), data.zone_name, colors["main_label"], fonts.main_label)
#        draw.text((base_x, int(msy * 0.11)), u"Эффект обороны \u25ba", colors["sub_main_label"], fonts.sub_main_label)

        if data.rating == "S":
            grade_lt, grade_bg = Others.s_let, Backgrounds.s_bg
        elif data.rating == "A":
            grade_lt, grade_bg = Others.a_let, Backgrounds.a_bg
        else:
            grade_lt, grade_bg = Others.b_let, Backgrounds.b_bg

        grade_lt = grade_lt.resize((int(msx * 0.02), int(msy * 0.06)))
        grade_bg = grade_bg.resize((grade_bg.size[0] // 2, grade_bg.size[1] // 2))
        bg.paste(grade_bg, (msx - grade_bg.size[0], 0, msx, grade_bg.size[1]), grade_bg)
        bg.paste(grade_lt, 
                 (msx - grade_lt.size[0] * 2, grade_lt.size[1] // 2, msx - grade_lt.size[0], int(grade_lt.size[1] * 1.5)), 
                 grade_lt)
        draw.text((msx - grade_lt.size[0], grade_lt.size[1] * 2), data.floor_challenge_time.strftime("%d.%m.%Y %H:%M:%S"),
                  colors["floor_challenge_time"], fonts.challenge_time, anchor="rt")
        
        #Avatars and nodes
        fnode_x = base_x
        half_x = msx // 2
        img_x = self.sizes.challenge_avatar[0]
        step = int(msx * 0.01)
        lwa_y = int(msy * 0.8)
        itime_y = int(msy * 0.85)
        for hind, node in enumerate((data.node_1, data.node_2)):
            for lind, avatar in enumerate(node.avatars):
                x = fnode_x + (step * lind) + (img_x * lind) + half_x * hind
                img = self.avatar_img(avatar, icons.avatars[avatar.id], self.sizes.challenge_avatar)
                bg.paste(img, (x, lwa_y - img.size[1], x + img_x, lwa_y))

            x += img_x + step
            buddy_img = self.buddy_img(node.buddy, icons.buddys[node.buddy.id], self.sizes.challenge_buddy)
            bg.paste(buddy_img, (x, lwa_y - buddy_img.size[1], x + buddy_img.size[0], lwa_y), buddy_img)

            bt = node.battle_time
            draw.text((int(msx * 0.32) + half_x * hind, itime_y), f"{bt // 3600:02} ч. {bt % 3600 // 60:02} мин. {bt % 60:02} сек.",
                      colors['battle_time'], fonts.battle_time)
            
            x += buddy_img.size[0]
            y = int(msy * 0.22)
            ge_img = self.challenge_rattrs(node.element_type_list)
            bg.paste(ge_img, (x - ge_img.size[0], y, x, y + ge_img.size[1]), ge_img)

            if paste_enemy_info:
                y = int(msx * 0.092)
                inimg = self.challenge_enemy_info.copy()
                bg.paste(inimg, (x - inimg.size[0], y, x, y + inimg.size[1]), inimg)

        return bg
    
    def challenge_rattrs(self, elements_id: list[int], round_corners_rad: int = 3) -> Image.Image:
        mix, miy = self.sizes.challenge
        icon_size = ((int(mix * 0.01) + int(miy * 0.04)) // 2,) * 2
        size = (int(mix * 0.145) + (icon_size[0] + 1) * len(elements_id), int(miy * 0.05))
        step = 1
        y = int(size[1] * 0.15)
        img = Image.new("RGBA", size, (0, 0, 0, 255))
        args = ((int(size[0] * 0.02), int(size[1] * 0.04)), "Рекомендуемые атрибуты", 
                self.colors["challenge"]['inner_label'], self.fonts.Challenge.inner_label)
        draw = ImageDraw.Draw(img)
        draw.text(*args)
        mx = int(draw.textbbox(args[0], args[1], args[3])[2])
        
        for i in range(len(elements_id)):
            x = mx + icon_size[0] * i + step * (i + 1)
            attr = Attributes.get(elements_id[i]).resize(icon_size)
            img.paste(attr, (x, y, x + icon_size[0], y + icon_size[0]), attr)
        
        return round_corners(img, round_corners_rad)
    
    def monsters_info(self, data: 'SDMonsterInfoStruct', icons: 'SDImagesStruct', round_corners_rad: int = 25) -> Image.Image:
        bg = self.monsters_info_bg
        mx, my = bg.size
        lvl = self.monsters_level(data)
        bg.paste(lvl, (int(mx * 0.6), int(my * 0.025), int(mx * 0.6) + lvl.size[0], int(my * 0.025) + lvl.size[1]), lvl)

        row = column = 0
        x, y = int(mx * 0.03), int(my * 0.1)
        x_off, y_off = int(mx * 0.04), int(my * 0.05)
        for monster in data.list:
            img = self.monster_image(monster, icons.monsters[monster.id])
            tx, ty = x + (img.size[0] * column) + (x_off * column), y + (img.size[1] * row) + (y_off * row)
            bg.paste(img, (tx, ty, tx + img.size[0], ty + img.size[1]), img)

            column ^= 1
            if not column:
                row += 1

        return round_corners(bg, round_corners_rad)

    def monsters_level(self, data: 'SDMonsterInfoStruct', round_corners_rad: int = 5, size: tuple[int, int] = (47, 20), 
                       color: tuple[int, int, int, float] = (82, 82, 82, 255), 
                       font: ImageFont.FreeTypeFont = ImageFont.truetype('arial.ttf', 12)) -> Image.Image:
        img = Image.new("RGBA", size, color)
        ImageDraw.Draw(img).text((size[0] * 0.15, size[1] * 0.2), f"Ур. {data.level}", font=font)
        return round_corners(img, round_corners_rad)
    
    def monster_image(self, data: 'SDMonsterStruct', icons: 'SDImgMonsterStruct', 
                      size: tuple[int, int] = (270, 130), font_path: str = 'res/fonts/inpin.ttf', 
                      text_color: tuple[int, int, int] = (80, 80, 80), round_corners_rad: int = 15) -> Image.Image:
        bg = Image.new("RGBA", size, (0, 0, 0, 255))

        insize = (int(size[0] * 0.29), int(size[1] * 0.84))
        micon = icons.icon.copy().resize(insize)
        icon_bg = icons.bg_icon.copy().resize(insize)
        race_icon = icons.race_icon.copy().resize((int(insize[0] * 0.4),) * 2)
        icon_bg.paste(micon, (0, 0, *insize), micon)
        icon_bg.paste(race_icon, (int(insize[0] * 0.6), int(insize[1] * 0.75), 
                                  int(insize[0] * 0.6) + race_icon.size[0], int(insize[1] * 0.75) + race_icon.size[1]), race_icon)
        icon_bg = round_corners(icon_bg, 3)

        bg.paste(icon_bg, (int(size[0] * 0.04), (size[1] - insize[1]) // 2, 
                           int(size[0] * 0.04) + insize[0], (size[1] - insize[1]) // 2 + insize[1]), icon_bg)

        mbg = self.monster_bg_image(icons.icon).resize((int(size[0] * 0.66), size[1]))
        bg.paste(mbg, (size[0] - mbg.size[0], 0, *size), mbg)

        sym_row = 15
        x_coo = int(size[0] * 0.37)
        font = ImageFont.truetype(font_path, size[0] * 0.056)
        draw = ImageDraw.Draw(bg)

        text1 = text2 = None
        if data.name[sym_row:]:
            for c in data.name[sym_row::-1]:
                if c in whitespace:
                    break
            if c not in whitespace:
                text1 = data.name[:sym_row - 3] + '...'
            else:
                ind = data.name[:sym_row].rfind(c)
                text1 = data.name[:ind]
                tmp = data.name[ind + 1:]
                text2 = tmp if len(tmp) < sym_row else tmp[:sym_row - 3] + '...'
        else:
            text1 = data.name

        if text1 and not text2:
            draw.text((x_coo, int(size[1] * 0.15)), text1, font=font)
        else:
            draw.text((x_coo, int(size[1] * 0.05)), text1, font=font)
            draw.text((x_coo, int(size[1] * 0.2)), text2, font=font)

        font = ImageFont.truetype(font_path, size[0] * 0.036)

        el_icon_size = (int(size[0] * 0.06),) * 2
        el_x_offset = el_icon_size[0] // 4
        weakness = []
        resist = []
        weak_y = int(size[1] * 0.45)
        resist_y = int(size[1] * 0.65)
        for weak, attr_id in zip((data.physics_weakness, data.fire_weakness, data.ice_weakness, data.elec_weakness, data.ether_weakness), 
                                 [*Attributes.alias_si.values()][:-1]):     #ignoring auric_inc
            if weak < 0:
                weakness.append(attr_id)
            if weak > 0:
                resist.append(attr_id)

        weak_text, resist_text = "Уязвимость:", "Устойчивость:"
        draw.text((x_coo, weak_y), weak_text + (' —' * (not len(weakness))), text_color, font)
        draw.text((x_coo, resist_y), resist_text + (' —' * (not len(resist))), text_color, font)

        x = int(draw.textbbox((x_coo, weak_y), weak_text, font)[2]) + el_icon_size[0] // 3
        for ind, attr_id in enumerate(weakness):
            attr = Attributes.get(attr_id).resize(el_icon_size)
            bg.paste(attr, (x, weak_y, x + el_icon_size[0], weak_y + el_icon_size[1]), attr)
            x += el_icon_size[0] + el_x_offset
        
        x = int(draw.textbbox((x_coo, resist_y), resist_text, font)[2]) + el_icon_size[0] // 3
        for ind, attr_id in enumerate(resist):
            attr = Attributes.get(attr_id).resize(el_icon_size)
            bg.paste(attr, (x, resist_y, x + el_icon_size[0], resist_y + el_icon_size[1]), attr)
            x += el_icon_size[0] + el_x_offset

        return round_corners(bg, round_corners_rad)
    
    def monster_bg_image(self, icon: Image.Image, brightness: float = 0.25) -> Image.Image:
        icon_w, icon_h = icon.size
        icon = icon.crop((0, icon_h * 0.25, icon_w, icon_h - icon_h * 0.25))
        *rgb, alpha = icon.split()
        arr = np.array(Image.merge('RGB', rgb)).astype(np.float32)
        gray = Image.fromarray(np.clip((arr * brightness).astype(np.uint8), 0, 255), 'RGB').convert('L')

        return fade_alpha(Image.merge('RGBA', (gray,) * 3 + (alpha,)))
