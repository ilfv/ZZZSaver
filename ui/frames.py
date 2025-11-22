from io import BytesIO
from typing import TYPE_CHECKING
from threading import Thread

import customtkinter as ctk
from cacheout import Cache
from PIL import Image, ImageTk

from lib.api import Api
from lib.lcache import LocalCache
from lib.image import ImageGen, SDImageGen
from lib.image.res.deadly_assault import ResBackgrounds
from lib.save_data import SavedData
from lib.utils import gdeadlyassault2pil_image, sdimgs2pil
from ui.utils import run_async, colored_text

if TYPE_CHECKING:
    from typing import Literal

    from lib.data_classes import DeadlyAssaultStruct, BufferStruct, ShiyuDefenseStruct, SDFloorDetailStruct, SDImagesStruct


class BuffFrame(ctk.CTkFrame):
    def __init__(self, master, data: 'BufferStruct', icon: Image.Image,
                 width: int = 300, height: int = 300, 
                 corner_radius: int | str | None = None, border_width: int | str | None = None, 
                 bg_color: str | tuple[str, str] | None = "transparent", fg_color: str | tuple[str, str] | None = None, 
                 border_color: str | tuple[str, str] | None = None, 
                 background_corner_colors: tuple[str | tuple[str, str]] | None = None, 
                 overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, 
                         border_width, bg_color, fg_color, border_color, 
                         background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.icon = icon.resize((50, 50))
        self.img = ImageTk.PhotoImage(self.icon)

        canv = ctk.CTkCanvas(self, width=50, height=50, highlightthickness=0, bg="#2b2b2b")
        canv.pack(side=ctk.LEFT, padx=5)
        canv.create_image(0, 0, image=self.img, anchor='nw')

        ctk.CTkLabel(self, text=data.name, anchor="e", font=("Arial bold", 20), text_color=f"#ffffff").pack(pady=5)

        text_box = ctk.CTkTextbox(self, width=width - 60, height=height - 60, font=("Arial", 15), wrap="word")
        colored_text(data.desc.replace("\\n", "\n"), text_box)
        text_box.pack()
        text_box.configure(state=ctk.DISABLED)


class BuffWindow(ctk.CTkToplevel):
    def __init__(self, data: 'list[BufferStruct]', icons: list[Image.Image], width=300, height=300):
        super().__init__()

        self.title("Buffs")
        self.geometry(f"{width}x{height}+1200+100")

        fc_range = range(len(data))
        if len(data) > 1:
            master = ctk.CTkScrollableFrame(self, width, height)
            master.pack()
            self.bind("<Up>", lambda _: master._parent_canvas.yview_scroll(-35, 'units'))
            self.bind("<Down>", lambda _: master._parent_canvas.yview_scroll(35, 'units'))
        else:
            master = self

        for i in fc_range:
            BuffFrame(master, data[i], icons[i], width=width - 20, height=height - 20).pack(pady=10)


class ShiyuDefenseBuffFrame(ctk.CTkFrame):
    def __init__(self, master, name: str, title_list: list[str], text_list: list[str], width = 200, height = 200, corner_radius = None, 
                 border_width = None, bg_color = "transparent", fg_color = None, border_color = None, background_corner_colors = None, 
                 overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, 
                         background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        
        ctk.CTkLabel(self, text=name, font=("arial bold", 12)).pack()
        for title, text in zip(title_list, text_list):
            ctk.CTkLabel(self, text=title, font=("arial italic", 10)).pack()
            textbox = ctk.CTkTextbox(self, wrap="word")
            colored_text(text.replace("\\n", "\n"), textbox)
            textbox.pack()


class ShiyuDefenseBuffWindow(ctk.CTkToplevel):
    def __init__(self, schedule_id: int, title: str = "Buff", geometry: tuple[int] = (300, 300, 800, 200), 
                 *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)

        data = SavedData().get_by_id("shiyu_defense", schedule_id)

        x, y = geometry[:2]
        self.size = geometry[:2]
        if geometry[2:]:
            xoff = geometry[2]
        else:
            xoff = 0
        if geometry[3:]:
            yoff = geometry[3]
        else:
            yoff = 0

        self.geometry(f"{x}x{y}" + (f"+{xoff}" if xoff else "") + (f"+{yoff}" if yoff else ""))
        self.title(title)

        sc_fr = ctk.CTkScrollableFrame(self)
        sc_fr.pack(expand=True, fill=ctk.BOTH)

        for floor in data.all_floor_detail:
            ShiyuDefenseBuffFrame(sc_fr, floor.zone_name, 
                                  (buff.title for buff in floor.buffs), (buff.text for buff in floor.buffs)).pack(pady=10)

class ShiyuDefenseEnemyFrame(ctk.CTkScrollableFrame):
    im_cache = Cache()

    def __init__(self, master, data: 'SDFloorDetailStruct', icons: 'SDImagesStruct', width = 600, height = 600, corner_radius = None, 
                 border_width = None, bg_color = "transparent", fg_color = None, border_color = None, background_corner_colors = None, 
                 overwrite_preferred_drawing_method = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, 
                         border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        ctk.CTkLabel(self, text=data.zone_name).pack()

        for node in [data.node_1, data.node_2]:
            key = str(node.monster_info)
            if key in self.im_cache:
                img = self.im_cache.get(key)
            else:
                img = SDImageGen().monsters_info(node.monster_info, icons)
                self.im_cache.set(key, img)
            
            ctk.CTkLabel(self, text='', image=ctk.CTkImage(img, size=img.size)).pack(pady=10)

class ShiyuDefenseEnemyWindow(ctk.CTkToplevel):
    def __init__(self, schedule_id: int, title: str = "Enemies", geometry: tuple[int] = (650, 600, 1000, 200), 
                 *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)

        data = SavedData().get_by_id("shiyu_defense", schedule_id)
        icons = sdimgs2pil(run_async(Api().shiyu_defense_imgs(data)))

        x, y = geometry[:2]
        self.size = geometry[:2]
        if geometry[2:]:
            xoff = geometry[2]
        else:
            xoff = 0
        if geometry[3:]:
            yoff = geometry[3]
        else:
            yoff = 0

        self.geometry(f"{x}x{y}" + (f"+{xoff}" if xoff else "") + (f"+{yoff}" if yoff else ""))
        self.title(title)

        sc_fr = ctk.CTkScrollableFrame(self)
        sc_fr.pack(expand=True, fill=ctk.BOTH)

        for floor in data.all_floor_detail:
            ShiyuDefenseEnemyFrame(sc_fr, floor, icons).pack(pady=10)


class BaseDetailWindow(ctk.CTkToplevel):
    def __init__(self, title: str = "Data", geometry: tuple[int] = (700, 600, 800, 200), *args, fg_color = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)

        x, y = geometry[:2]
        self.size = geometry[:2]
        if geometry[2:]:
            xoff = geometry[2]
        else:
            xoff = 0
        if geometry[3:]:
            yoff = geometry[3]
        else:
            yoff = 0

        self.geometry(f"{x}x{y}" + (f"+{xoff}" if xoff else "") + (f"+{yoff}" if yoff else ""))
        self.title(title)
        self.lab = ctk.CTkLabel(self, text="", image=ctk.CTkImage(ResBackgrounds.empty_img, size=ResBackgrounds.empty_img.size))
        self.lab.pack()
    
    def init(*args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def handler(cls, zone_id: int) -> None:
        obj = cls()
        Thread(target=obj.init, args=(zone_id,), daemon=True).start()


class DADetailWindow(BaseDetailWindow):
    def __init__(self, title: str = "Data", geometry: tuple[int] = (700, 600, 800, 200), *args, fg_color = None, **kwargs):
        super().__init__(*args, title=title, geometry=geometry, fg_color=fg_color, **kwargs)

    def init(self, zone_id: int):
        data = SavedData().get_by_id("deadly_assault", zone_id)

        if data and data.has_data:
            icons = gdeadlyassault2pil_image(run_async(Api().deadlyassault_imgs(data)))
        else:
            icons = None
        self.img = ImageTk.PhotoImage(ImageGen().generate(data, icons).resize(self.size))

        self.lab.destroy()

        can = ctk.CTkCanvas(self, width=self.size[0], height=self.size[1], highlightthickness=0)
        can.pack(expand=True, fill=ctk.BOTH)
        can.create_image(0, 0, image=self.img, anchor="nw")

        for i in range(3):
            it = can.create_text(640, 205 + (140 * i), text="Buff", font=("Arial bold italic", 15), fill="#838383")
            can.tag_bind(it, "<Button-1>", lambda _, num=i: BuffWindow(data.list[num].buffer, icons.challenges[num].buff))


class SDDetailWindow(BaseDetailWindow):
    def __init__(self, title = "Data", geometry = (800, 600, 800, 100), *args, fg_color=None, **kwargs):
        super().__init__(title, geometry, *args, fg_color=fg_color, **kwargs)

    def init(self, schedule_id: int):
        data = SavedData().get_by_id("shiyu_defense", schedule_id)

        if data.has_data:
            icons = sdimgs2pil(run_async(Api().shiyu_defense_imgs(data)))
        else:
            icons = None
        img = SDImageGen().generate(data, icons)
        self.img = ctk.CTkImage(img.resize((self.size[0], img.size[1])), size=(self.size[0], img.size[1]))

        self.lab.destroy()

        height = 60
        btn_frame = ctk.CTkFrame(self, width=self.size[0], height=height)
        btn_frame.pack(expand=True, fill=ctk.BOTH)
        ctk.CTkButton(btn_frame, width=self.size[0] // 4, height=40, text="Buff", fg_color="#2b2b2b",
                      font=("Arial bold italic", 20), text_color="#838383", 
                      command=lambda: ShiyuDefenseBuffWindow(schedule_id)).place(x=self.size[0] // 5, y=height // 4)
        ctk.CTkButton(btn_frame, width=self.size[0] // 4, height=40, text="Enemy", fg_color="#2b2b2b",
                      font=("Arial bold italic", 20), text_color="#838383", 
                      command=lambda: ShiyuDefenseEnemyWindow(schedule_id)).place(x=self.size[0] // 2, y=height // 4)

        can = ctk.CTkScrollableFrame(self, width=self.size[0], height=self.size[1])
        can.pack(expand=True, fill=ctk.BOTH)
        ctk.CTkLabel(can, img.size[0], img.size[1], text='', image=self.img).pack()


class MMenuScrollableFrame(ctk.CTkScrollableFrame):
    labels: list[ctk.CTkLabel]

    def __init__(self, master, 
                 width: int = 600, 
                 height: int = 550, 
                 corner_radius: int | str | None = None, 
                 border_width: int | str | None = None, 
                 bg_color: str | tuple[str, str] = "transparent", 
                 fg_color: str | tuple[str, str] = None, 
                 border_color: str | tuple[str, str] = None, 
                 scrollbar_fg_color: str | tuple[str, str] = None, 
                 scrollbar_button_color: str | tuple[str, str] = None, 
                 scrollbar_button_hover_color: str | tuple[str, str] = None, 
                 label_fg_color: str | tuple[str, str] = None, 
                 label_text_color: str | tuple[str, str] = None, 
                 label_text: str = "Сохраненная информация:", 
                 label_font: tuple | ctk.CTkFont | None = ("Arial bold", 15), 
                 label_anchor: str = "center", 
                 orientation: "Literal['vertical', 'horizontal']" = "vertical"):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, 
                         scrollbar_fg_color, scrollbar_button_color, scrollbar_button_hover_color, 
                         label_fg_color, label_text_color, label_text, label_font, label_anchor, orientation)
        self.im_cache = Cache()
        self.labels = []

    def update_info(self, mode_name: str, size: tuple[int, int] = (600, 180)) -> None:
        collection = SavedData().get(mode_name)
        local_cache = LocalCache()
        for label in self.labels:
            label.destroy()

        if mode_name == "deadly_assault":
            model: 'DeadlyAssaultStruct'
            for i in range(len(collection)):
                model = collection[i]
                if f"d{model.zone_id}" in self.im_cache:
                    img = self.im_cache.get(f"d{model.zone_id}")
                else:
                    if model.avatar_icon in local_cache:
                        avatar_icon = Image.open(BytesIO(local_cache.get(model.avatar_icon)))
                    else:
                        avatar_icon = None

                    img = ImageGen().main_info_st(model, avatar_icon, 
                                                  add_sub_text="> Подробнее" if model.has_data else "").resize(size)
                    self.im_cache.set(f"d{model.zone_id}", img)
                    
                lab = ctk.CTkLabel(self, text="", image=ctk.CTkImage(img, size=img.size))
                lab.pack(pady=10)
                self.labels.append(lab)

                if model.has_data:
                    lab.bind("<Button-1>", lambda _, mid=model.zone_id: DADetailWindow.handler(mid))

        elif mode_name == "shiyu_defense":
            model: 'ShiyuDefenseStruct'
            for i in range(len(collection)):
                model = collection[i]
                if f"s{model.schedule_id}" in self.im_cache:
                    img = self.im_cache.get(f"s{model.schedule_id}")
                else:
                    img = SDImageGen().main_info_st(model).resize(size)
                    self.im_cache.set(f"s{model.schedule_id}", img)

                lab = ctk.CTkLabel(self, text="", image=ctk.CTkImage(img, size=(img.size[0] - 25, img.size[1] - 50)))
                lab.pack(pady=10)
                self.labels.append(lab)

                if model.has_data:
                    lab.bind("<Button-1>", lambda _, mid=model.schedule_id: SDDetailWindow.handler(mid))

 
class RadioFrame(ctk.CTkFrame):
    init_num = 0
    modes = ["deadly_assault", "shiyu_defense"]
    names = ["Опасный штурм", "Оборона Шиюй"]

    def __init__(self, master, info_frame: MMenuScrollableFrame, width: int = 600, height: int = 70, 
                 btn_height: int = 15, btn_width: int = 15, btn_corner_radius: int = 15,
                 corner_radius: int | str | None = None, border_width: int | str | None = None, 
                 bg_color: str | tuple[str, str] = "transparent", fg_color: str | tuple[str, str] = None, 
                 border_color: str | tuple[str, str] = None, 
                 background_corner_colors: tuple[str | tuple[str, str]] | None = None, 
                 overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, 
                         bg_color, fg_color, border_color, background_corner_colors, 
                         overwrite_preferred_drawing_method, **kwargs)
        
        self.info_frame = info_frame
        
        buttons = [ctk.CTkRadioButton(self, height=height // 2, radiobutton_height=btn_height, radiobutton_width=btn_width, 
                                      corner_radius=btn_corner_radius, text=self.names[i], 
                                      font=("Arial bold", 15), command=lambda num=i: self.update_val(num))
                        for i in range(2)]
        self.buttons = buttons
        
        self.last_set = self.init_num
        buttons[self.init_num].select()
        self.info_frame.update_info(self.modes[self.init_num])

        for i in range(2):
            buttons[i].place(x=int(width * 0.3), y=height // 2 * i)

    def update_val(self, ind: int) -> None:
        if ind != self.last_set:
            self.info_frame.update_info(self.modes[ind])
            self.buttons[self.last_set].deselect()
            self.last_set = ind
        
