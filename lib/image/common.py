from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from lib.data_classes import AvatarStruct
from lib.utils import singleton

from .res import Grades, Others
from .utils import round_corners

if TYPE_CHECKING:
    from lib.data_classes import GIBossStruct, BuddyStruct


@singleton
class ImageGen:
    def __init__(self):
        self.boss_images_sizes = ((300, 300), (300, 300), (50, 50))
    
    def avatar_img(self, data: AvatarStruct, 
                        icon: Image.Image, 
                        resize: tuple[int, int] | None = (75, 75)) -> Image.Image:
        icon = icon.copy()
        icon = icon.resize(resize) if resize else icon
        rarity_icon: Image.Image = getattr(Grades, data.rarity.lower())
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

        bg = Others.buddy_bg.copy()
        bg.paste(buddy, (0, 0, 240, 240), buddy)

        bg = bg.resize(resize) if resize else bg
        grade = (Grades.s if data.rarity == "S" else Grades.a).resize((15, 15))
        
        bg.paste(grade, (2, 2, 17, 17), grade)
        return round_corners(bg, 3)
    
    def boss_bg_img(self, data: 'GIBossStruct', 
                    bbox: tuple[int, int, int, int] = (50, 0, 300, 80)) -> Image.Image:
        img = data.icon.resize((300, 300)).crop(bbox)
        *rgb, alpha = img.split()
        gray = Image.merge("RGB", rgb).convert("L")


        return Image.merge("RGBA", (*Image.merge("RGB", (gray, gray, gray)).split(), alpha))
