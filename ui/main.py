import sys; sys.path.append(".")
from tkinter import messagebox
from typing import TYPE_CHECKING

import customtkinter as ctk

from lib.api import Api
from lib.save_data import SavedData
from ui.frames import DATotalFrame, DetailFrame
from ui.utils import run_async

if TYPE_CHECKING:
    from typing import Callable

ctk.set_appearance_mode("dark")


def da_total_btn(frame: DetailFrame) -> 'Callable[[int], None]':
    def handle(zone_id: int):
        frame.elements_update(zone_id)
    
    return handle


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zzz хелпер")
        self.geometry("1050x600")
        self.resizable(False, False)

        self.scrollbar = ctk.CTkScrollableFrame(self, 
                                                width=400, 
                                                height=475, 
                                                label_text="Сохраненная информация:",
                                                label_font=("Arial bold", 15))
        self.scrollbar.place(x=0, y=60)

        self.detail_frame = DetailFrame(self)
        self.detail_frame.place(x=440, y=0)

        for model in SavedData():
            DATotalFrame(self.scrollbar, model, da_total_btn(self.detail_frame)).pack(pady=10)


if __name__ == "__main__":
    try:
        run_async(Api().update_saved_data())
    except Exception as exc:
        messagebox.showerror("Error while updating data", exc)

    try:
        App().mainloop()
    except Exception as exc:
        messagebox.showerror("Error", exc)
