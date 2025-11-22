import sys
import atexit
import traceback

import customtkinter as ctk

from lib.api import Api
from lib.save_data import SavedData
from lib.settings import Config
from lib.logger import get_logger
from ui.frames import RadioFrame, MMenuScrollableFrame
from ui.utils import run_async, parse_args

_config = Config().get()
_log = get_logger(__file__, "Main")
ctk.set_appearance_mode("dark")





class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zzz хелпер")
        self.geometry("600x675")
        self.resizable(False, False)

        scrollbar = MMenuScrollableFrame(self)
        scrollbar.place(x=0, y=70)

        radio = RadioFrame(self, info_frame=scrollbar)
        radio.place(x=0, y=0)

    def exit(self):
        if _config.api.auto_update_cookies:
            _config.headers["Cookie"].update_saved()


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    try:
        if args.dusd: 
            run_async(Api().update_saved_data())
            SavedData().save2json()
    except Exception as exc:
        _log.error("Error while updating data:\n" + traceback.format_exc())

    app = App()
    atexit.register(app.exit)

    try:
        app.mainloop()
    except Exception as exc:
        text = "Error:\n" + traceback.format_exc()
        _log.error(text)
