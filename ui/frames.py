from typing import TYPE_CHECKING

import customtkinter as ctk
from PIL import ImageTk

from lib.api import Api
from lib.image import ImageGen
from lib.save_data import SavedData
from lib.image.res import Stars, Others
from ui.utils import bytes2pil_tk_image, imgres2pil_images, run_async

if TYPE_CHECKING:
    from typing import Callable
    from lib.data_classes import DeadlyAssaultStruct, ChallengeResultStruct


class DATotalFrame(ctk.CTkFrame):
    def __init__(self, master,
                 data: 'DeadlyAssaultStruct',
                 handle: 'Callable[[int], None] | None',
                 inc_detail_btn: bool = True,
                 corner_radius: int | str | None = None, 
                 border_width: int | str | None = None, 
                 bg_color: str | tuple[str, str] = "#2B2B2B",
                 fg_color: str | tuple[str, str] = None, 
                 border_color: str | tuple[str, str] = None, 
                 background_corner_colors: tuple[str | tuple[str, str]] | None = None, 
                 overwrite_preferred_drawing_method: str | None = None, **kwargs):
        width, height = 400, 100

        super().__init__(master, 
                         width, 
                         height, 
                         corner_radius, 
                         border_width, 
                         bg_color, 
                         fg_color, 
                         border_color, 
                         background_corner_colors, 
                         overwrite_preferred_drawing_method, **kwargs)

        self.imgs = [bytes2pil_tk_image(run_async(Api().get_img(data.avatar_icon)), (20, 20)),
                     ImageTk.PhotoImage(Others.dark_bg),
                     ImageTk.PhotoImage(Stars.light_star.resize((20, 20)))]

        self.canv = canvas = ctk.CTkCanvas(self, highlightthickness=0, width=width, height=height, bg=bg_color)
        start_time_str = data.start_time.to_datetime().strftime("%d.%m.%Y")
        end_time_str = data.end_time.to_datetime().strftime("%d.%m.%Y")
        canvas.pack(fill=ctk.BOTH, expand=True)

        canvas.create_image(0, 0, image=self.imgs[1], anchor="nw")
        canvas.create_text(200, 8, text="Общий счет", font=("Arial", 13), fill="#ffffff")
        canvas.create_text(200, 35, text=data.total_score, font=('Arial bold', 20), fill="#d8d8d8")
        canvas.create_image(185, 60, image=self.imgs[2])
        canvas.create_text(210, 60, text=f"x{data.total_star}", font=("Arial", 15), fill="#ffffff")
        canvas.create_image(160, 85, image=self.imgs[0])
        canvas.create_text(220, 85, text=data.nick_name, fill="#ffffff")
        
        canvas.create_text(55, 5, text="Период подсчёта:", fill="#8F8F8F", font=("Arial", 9))
        canvas.create_text(62, 20, text=f"{start_time_str} - {end_time_str}", fill="#8f8f8f")

        if inc_detail_btn:
            txt = canvas.create_text(350, 10, text="Подробнее ▶", fill="#acacac", font=("Arial", 12))
            canvas.tag_bind(txt, "<Button-1>", lambda _: handle(data.zone_id))
    

class ChallengeFrame(ctk.CTkFrame):
    def __init__(self, master, 
                 data: 'ChallengeResultStruct',
                 corner_radius: int | str | None = None, 
                 border_width: int | str | None = None, 
                 bg_color: str | tuple[str, str] = "#2B2B2B", 
                 fg_color: str | tuple[str, str] = None, 
                 border_color: str | tuple[str, str] = None, 
                 background_corner_colors: tuple[str | tuple[str, str]] = None, 
                 overwrite_preferred_drawing_method: str | None = None, **kwargs):
        
        width, height = 600, 150

        super().__init__(master, 
                         width, 
                         height, 
                         corner_radius, 
                         border_width, 
                         bg_color, 
                         fg_color, 
                         border_color, 
                         background_corner_colors, 
                         overwrite_preferred_drawing_method, **kwargs)
        
        self.giimages = imgres2pil_images(run_async(Api().get_cres_images(data)))

        self.imgs = [ImageTk.PhotoImage(Others.det_card_bg), 
                     ImageTk.PhotoImage(ImageGen().boss_img(self.giimages.boss[0])),
                     [ImageTk.PhotoImage(ImageGen().avatar_img(data.avatar_list[i], self.giimages.avatars[i]))
                      for i in range(3)],
                     ImageTk.PhotoImage(ImageGen().boss_bg_img(self.giimages.boss[0])),
                     ImageTk.PhotoImage(Stars.dark_star), ImageTk.PhotoImage(Stars.light_star)]

        boss_name = data.boss[0].name
        canvas = ctk.CTkCanvas(self, width=width, height=height, highlightthickness=0, bg=bg_color)
        canvas.pack(fill=ctk.BOTH, expand=True)

        canvas.create_image(0, 0, image=self.imgs[0], anchor='nw')
        canvas.create_image(5, 5, image=self.imgs[1], anchor="nw")
        canvas.create_text(250, 25, 
                           text=f"{boss_name[:26]}..." if len(boss_name) > 25 else boss_name, 
                           fill="#ffffff", font=("Arial bold", 13), justify="center")

        xoffset = 160
        for i in range(3):
            canvas.create_image(xoffset, 105, image=self.imgs[2][i])
            xoffset += 85
        
        canvas.create_text(245, 55, text=f"Время прохождения: {data.challenge_time.to_datetime().strftime("%d.%m.%Y %H:%M:%S")}",
                           fill="#8f8f8f", font=("Arial", 10))
        canvas.create_image(400, 60, image=self.imgs[3], anchor="nw")
        
        xoffset = 430
        for i in range(1, 4):
            canvas.create_image(xoffset, 75, image=self.imgs[4 + (i <= data.star)])
            xoffset += 24
        
        text = canvas.create_text(455, 105, text=data.score, font=("Arial bold", 20), fill="#ffffff")
        bbox = canvas.bbox(text)
        rec = canvas.create_rectangle(bbox, fill="#2b2b2b")
        canvas.tag_raise(text, rec)


class DetailFrame(ctk.CTkFrame):
    def __init__(self, master,  
                 corner_radius: int | str | None = None, 
                 border_width: int | str | None = None, 
                 bg_color: str | tuple[str, str] = "transparent", 
                 fg_color: str | tuple[str, str] = None, 
                 border_color: str | tuple[str, str] = None, 
                 background_corner_colors: tuple[str | tuple[str, str]] = None, 
                 overwrite_preferred_drawing_method: str | None = None, **kwargs):
        width, height = 600, 600
        super().__init__(master, 
                         width, 
                         height, 
                         corner_radius, 
                         border_width, 
                         bg_color, 
                         fg_color, 
                         border_color, 
                         background_corner_colors, 
                         overwrite_preferred_drawing_method, **kwargs)
        self.current_zid = None
        self.frames: list[ctk.CTkFrame] = []

    def elements_update(self, zone_id: int):
        if self.current_zid == zone_id:
            return
        self.current_zid = zone_id
        
        for frame in self.frames:
            frame.destroy()

        data = SavedData().get_by_id(zone_id)

        main_info = DATotalFrame(self, data, None, False)
        main_info.pack(padx=100)

        self.frames.append(main_info)
        for challenge in data.list:
            ch = ChallengeFrame(self, challenge)
            ch.pack(pady=5)
            self.frames.append(ch)
