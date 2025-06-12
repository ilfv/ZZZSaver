from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from lib.utils import singleton

from .res import GRGrades, GRBackgrounds, TgResStars, TgResBackgrounds, Stars
from .utils import round_corners, fade_alpha

if TYPE_CHECKING:
    from lib.data_classes import (DeadlyAssaultStruct, ChallengeResultStruct, AvatarStruct, BuddyStruct, 
                                  GDeadlyAssaultImgsStruct, GIBossStruct, GetImagesReturnStruct)


class YSizes:
    main_info = 260
    main_info_pad = -25     #after resize

    challenge_info = 150
    challenge_info_pad = 25


@singleton
class ImageGen:
    def __init__(self):
        self.boss_images_sizes = ((300, 300), (300, 300), (50, 50))

    def generate(self, data: 'DeadlyAssaultStruct', icons: 'GDeadlyAssaultImgsStruct', font_path: str = "res/fonts/inpin.ttf") -> Image.Image:
        self.font_path = font_path

        self.img = TgResBackgrounds.dark_bg.copy()
        self.img.paste(TgResBackgrounds.main_info_bg, (0, 0) + TgResBackgrounds.main_info_bg.size)

        self.draw = ImageDraw.Draw(self.img)

        self.icons = icons
        self.yoffset = 0

        self.main_info(data, icons)
        self.img = self.img.resize((950, 750)).convert("RGBA")
        self.draw = ImageDraw.Draw(self.img)
        self.yoffset += YSizes.main_info + YSizes.main_info_pad

        for i in range(3):
            self.challenge_info(data.list[i], icons.challenges[i])
            self.yoffset += YSizes.challenge_info + YSizes.challenge_info_pad

        return self.img
    
    def main_info(self, data: 'DeadlyAssaultStruct', icons: 'GDeadlyAssaultImgsStruct', yoffset: int | None = None) -> None:
        half_x = self.img.size[0] // 2
        avatar_icon = icons.avatar_icon.resize((50, 50))
        start_time = data.start_time.to_datetime().strftime("%d.%m.%Y")
        end_time = data.end_time.to_datetime().strftime("%d.%m.%Y")
        if not yoffset:
            yoffset = self.yoffset

        self.draw.text((50, 50), text=f"Период подсчета: {start_time} - {end_time}",
                       fill=(100, 100, 100), font=ImageFont.truetype("arial.ttf", 25))
        self.draw.text((half_x - 115, yoffset + 45), text="Общий счёт", font=ImageFont.truetype(self.font_path, 30))
        self.draw.text((half_x - 75, yoffset + 80), text=str(data.total_score), font=ImageFont.truetype(self.font_path, 50))
        self.img.paste(Stars.light_star, 
                       (half_x - Stars.light_star.size[0] - 20, yoffset + 150, 
                        half_x - 20, yoffset + 150 + Stars.light_star.size[1]), 
                       Stars.light_star)
        self.draw.text((half_x - 10, yoffset + 150), f"x{data.total_star}",
                        font=ImageFont.truetype(self.font_path, 35))
        
        yoffset = yoffset + 150 + Stars.light_star.size[1]
        self.img.paste(avatar_icon, 
                       (half_x - avatar_icon.size[0] - 110, yoffset + 10, half_x - 110, yoffset + avatar_icon.size[1] + 10),
                       avatar_icon)
        self.draw.text((half_x - 90, yoffset + avatar_icon.size[1] // 2 - 10), text=data.nick_name, 
                       font=ImageFont.truetype("arial.ttf", 30))
    
    def challenge_info(self, data: 'ChallengeResultStruct', icons: 'GetImagesReturnStruct'):
        fpadx = 25
        self.img.paste(TgResBackgrounds.det_card_bg, 
                       (25, self.yoffset, TgResBackgrounds.det_card_bg.size[0] + 25, 
                        self.yoffset + TgResBackgrounds.det_card_bg.size[1]),
                       TgResBackgrounds.det_card_bg)
        boss_img = self.boss_img(data=icons.boss[0])
        self.img.paste(boss_img, 
                       (fpadx + 5, self.yoffset + 5, boss_img.size[0] + fpadx + 5, self.yoffset + boss_img.size[1] + 5),
                       boss_img)
        padx = boss_img.size[0] + fpadx
        self.draw.text((padx + 20, self.yoffset + 5), text=data.boss[0].name, font=ImageFont.truetype(self.font_path, 25))
        self.draw.text((padx + 15, self.yoffset + 45), 
                       text=f"Время прохождения {data.challenge_time.to_datetime().strftime("%d.%m.%Y %H:%M:%S")}",
                       fill=(80, 80, 80), font=ImageFont.truetype("arial.ttf", 18))
        
        xoffset = (0, 90, 180)
        for i in range(3):
            avatar = self.avatar_img(data.avatar_list[i], icons.avatars[i])
            self.img.paste(avatar, 
                           (xoffset[i] + padx + 15, self.yoffset + 70, xoffset[i] + padx + 90, self.yoffset + 145),
                           avatar)
        
        buddy = self.buddy_img(data.buddy, icons.buddy)
        xoffset = xoffset[2] + padx + 105
        self.img.paste(buddy, (xoffset, self.yoffset + 85, xoffset + buddy.size[0], self.yoffset + buddy.size[1] + 85), buddy)

        boss_bg_img = self.boss_bg_img(icons.boss[0], (100, 0, 500, 100), (500, 500))
        det_card_size = TgResBackgrounds.det_card_bg.size
        det_bg_coords = (det_card_size[0] + fpadx, det_card_size[1] + self.yoffset)
        self.img.paste(boss_bg_img, 
                       tuple(det_bg_coords[i] - boss_bg_img.size[i] - 5 for i in range(2)) + tuple(coo - 5 for coo in det_bg_coords),
                       boss_bg_img)
        
        xoffset = det_bg_coords[0] - boss_bg_img.size[0] - 5
        star_size = TgResStars.light_star.size
        for i in range(data.total_star):
            st_x = xoffset + (star_size[0] * i)
            self.img.paste((TgResStars.dark_star, TgResStars.light_star)[data.star >= (i + 1)], 
                           (st_x, self.yoffset + 65, st_x + star_size[0], self.yoffset + star_size[1] + 65),
                           TgResStars.light_star)
        
        self.draw.text((xoffset, self.yoffset + 90), text=f"{data.score}", fill=(210, 210, 210), 
                       font=ImageFont.truetype(self.font_path, 40))
        
    
    def avatar_img(self, data: 'AvatarStruct', 
                        icon: Image.Image,  
                        resize: tuple[int, int] | None = (75, 75)) -> Image.Image:
        icon = icon.copy()
        icon = icon.resize(resize) if resize else icon
        rarity_icon: Image.Image = getattr(GRGrades, data.rarity.lower())
        icon.paste(rarity_icon, (2, 2, 20, 20), rarity_icon)

        if data.rank:
            overlay = Image.new("RGBA", icon.size, (0, 0, 0, 0))
            draw = ImageDraw.ImageDraw(overlay)
            draw.rectangle(((55, 0), (75, 20)), fill=(0, 0, 0, 127), outline=None)
            draw.text((61, 2), str(data.rank), font=ImageFont.truetype("arial.ttf", 15))
            icon = Image.alpha_composite(icon, overlay)
        
        return round_corners(icon, 3)

    def boss_img(self, data: 'GIBossStruct', resize: tuple[int, int] | None = (110, 140)) -> Image.Image:
        bg_size, boss_icon_size, race_icon_size = self.boss_images_sizes
        bg_icon = data.bg_icon.resize(bg_size)
        icon = data.icon.resize(boss_icon_size)
        race_icon = data.race_icon.resize(race_icon_size)
        
        bg_icon.paste(icon, 
                      tuple(bg_size[i] - boss_icon_size[i] for i in range(2)) + bg_size, 
                      icon)
        bg_icon.paste(race_icon, 
                      tuple(bg_size[i] - race_icon_size[i] for i in range(2)) + bg_size, 
                      race_icon)

        return round_corners(bg_icon.resize(resize) if resize else bg_icon, 15)
    
    def buddy_img(self, data: 'BuddyStruct', icon: Image.Image, 
                  resize: tuple[int, int] | None = (60, 60)) -> Image.Image:
        offset = 70
        buddy = icon.copy().convert("RGBA").crop((offset, offset, 240 + offset, 240 + offset))

        bg = GRBackgrounds.buddy_bg.copy()
        bg.paste(buddy, (0, 0, 240, 240), buddy)

        bg = bg.resize(resize) if resize else bg
        grade = (GRGrades.s if data.rarity == "S" else GRGrades.a).resize((15, 15))
        
        bg.paste(grade, (2, 2, 17, 17), grade)
        return round_corners(bg, 3)
    
    def boss_bg_img(self, data: 'GIBossStruct', 
                    bbox: tuple[int, int, int, int] = (50, 0, 300, 80),
                    resize: tuple[int, int] = (300, 300)) -> Image.Image:
        img = data.icon.resize(resize).crop(bbox)
        *rgb, alpha = img.split()
        gray = Image.merge("RGB", rgb).convert("L")

        return fade_alpha(Image.merge("RGBA", (*Image.merge("RGB", (gray, gray, gray)).split(), alpha)))
