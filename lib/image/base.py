from functools import cached_property
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from lib.image.res.deadly_assault import ResBackgrounds as DAResBackgrounds
from lib.image.res.shiyu_defense import Backgrounds
from lib.image.res.elements import Attributes, Professions
from lib.image.res.others import Grades
from lib.image.utils import round_corners

if TYPE_CHECKING:
    from lib.data_classes.api import AvatarStruct, BuddyStruct


class BaseGen:
    def avatar_img(self, data: 'AvatarStruct', 
                         icon: Image.Image,  
                         size: tuple[int, int] = (75, 75),
                         add_bg: bool = True,
                         draw_elements: bool = True,
                         draw_bottom_line: bool = True,
                         font: ImageFont.FreeTypeFont | tuple = ImageFont.truetype("arial.ttf", 17)) -> Image.Image:
        if isinstance(font, tuple):
            font = ImageFont.truetype(font[0], font[1])

        icon = icon.copy()

        if draw_bottom_line:
            bottom_line_size = (size[0], int(size[1] * 0.2))
            icon = icon.resize((size[0], size[1] - bottom_line_size[1]))
        else:
            icon = icon.resize(size)
            bottom_line_size = None

        icon_size = icon.size
        ricon_size = (int(icon_size[0] * 0.24), int(icon_size[1] * 0.24))
        rix, riy = int(icon_size[0] * 0.02), int(icon_size[1] * 0.02)
        rarity_icon: Image.Image = getattr(Grades, data.rarity.lower() + "_rank").resize(ricon_size)
        icon.paste(rarity_icon, (rix, riy, rix + ricon_size[0], riy + ricon_size[1]), rarity_icon)

        if data.rank:
            overlay = Image.new("RGBA", icon.size, (0, 0, 0, 0))
            draw = ImageDraw.ImageDraw(overlay)
            draw.rectangle(((int(icon_size[0] * 0.73), 0), (icon_size[0], int(icon_size[1] * 0.26))), fill=(0, 0, 0, 127), outline=None)
            draw.text((int(icon_size[0] * 0.81), int(icon_size[0] * 0.02)), str(data.rank), 
                      font=ImageFont.truetype("arial.ttf", int(icon_size[0] * 0.2)))
            icon = Image.alpha_composite(icon, overlay)

        if draw_elements:
            el_size = (int(icon_size[0] * 0.15), int(icon_size[1] * 0.15))
            attr = Attributes.get_by_id(data.id, data.element_type).resize(el_size)
            profession = Professions.get(data.avatar_profession).resize(el_size)

            bg = Image.new("RGBA", (int(icon_size[0] * 0.18), int(icon_size[1] * 0.18)), (0, 0, 0, 0))
            bgx, bgy = bg.size
            ImageDraw.Draw(bg).ellipse((0, 0, int(bgx * 0.9), int(bgy * 0.9)), (0, 0, 0, 255))
            bg2 = bg.copy()

            x, sy = int(size[0] * 0.03), int(size[1] * 0.25)
            ix, iy = (bgx - el_size[0]) // 2, (bgy - el_size[1]) // 2
            bbox = (ix, iy, ix + el_size[0], iy + el_size[1])

            bg.paste(attr, bbox, attr)
            icon.paste(bg, (x, sy, x + bgx, sy + bgy), bg)
            
            sy = sy + bgy + int(bgx * 0.1)
            bg2.paste(profession, bbox, profession)
            icon.paste(bg2, (x, sy, x + bgx, sy + bgy), bg2)

        if add_bg:
            tm = Backgrounds.avatar_bg.copy().resize(icon.size)
            tm.paste(icon, (0, 0) + icon.size, icon)
            icon = tm
        
        if draw_bottom_line:
            bg = Image.new("RGBA", size, (0, 0, 0, 255))
            ImageDraw.Draw(bg).text((bottom_line_size[0] // 3.5, icon_size[1] + bottom_line_size[1] // 8),
                                    f"Ур. {data.level}", (255, 255, 255), font=font)

            bg.paste(icon, (0, 0, *icon_size))
            icon = bg
        
        return round_corners(icon, int(size[0] * 0.04))
    
    def buddy_img(self, data: 'BuddyStruct', icon: Image.Image, 
                  out_size: tuple[int, int] = (60, 60),
                  work_size: tuple[int, int] = (240, 240),
                  crop_offset: int = 70,
                  text_color: tuple[int, int, int] = (255, 255, 255),
                  font: ImageFont.FreeTypeFont | tuple[str, int] = ImageFont.truetype("arial.ttf", 17),
                  draw_bottom_line: bool = True,
                  bottom_line_height: int = 20) -> Image.Image:
        buddy = icon.copy().convert("RGBA").crop((crop_offset, crop_offset, work_size[0] + crop_offset, work_size[0] + crop_offset))

        if isinstance(font, tuple):
            font = ImageFont.truetype(*font)

        bg = Backgrounds.buddy_bg.resize(work_size)
        bg.paste(buddy, (0, 0) + work_size, buddy)

        bg = bg.resize((out_size[0], out_size[1] - bottom_line_height * draw_bottom_line))
        grade = (Grades.s_rank if data.rarity == "S" else Grades.a_rank).resize((out_size[0] // 4, out_size[1] // 4))
        
        xoff, yoff = int(grade.size[0] * 0.03), int(grade.size[1] * 0.03)
        bg.paste(grade, (xoff, yoff, xoff + grade.size[0], yoff + grade.size[1]), grade)

        if draw_bottom_line:
            nbg = Image.new("RGBA", (bg.size[0], bg.size[1] + bottom_line_height), (0, 0, 0, 255))
            nbg.paste(bg, (0, 0) + bg.size, bg)

            ImageDraw.Draw(nbg).text((nbg.size[0] // 4.5, bg.size[1] + bottom_line_height // 15), f"Ур. {data.level}", 
                                     text_color, font)
            bg = nbg

        return round_corners(bg, int(out_size[0] * 0.05))
    
    @cached_property
    def empty_img(self) -> Image.Image:
        img = Image.new("RGBA", (1000, 1000), "#1d1f1e")
        empty_img = DAResBackgrounds.empty_img
        mhalf_size = tuple(i // 2 for i in img.size)
        ihalf_size = tuple(i // 2 for i in empty_img.size)
        img.paste(empty_img, 
                  (mhalf_size[0] - ihalf_size[0], mhalf_size[1] - ihalf_size[1],
                   mhalf_size[0] + ihalf_size[0], mhalf_size[1] + ihalf_size[1]),
                   empty_img)
        
        ImageDraw.Draw(img).text((mhalf_size[0] - ihalf_size[0] + 30, mhalf_size[1] + ihalf_size[1] + 10),
                                 "Нет данных об испытаниях", 
                                 font=ImageFont.truetype("arial.ttf", 30),
                                 fill=(200, 200, 200))

        return img
