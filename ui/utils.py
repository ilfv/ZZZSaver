import re
import asyncio
import argparse
from threading import Thread
from typing import TYPE_CHECKING, TypeVar

import customtkinter as ctk

if TYPE_CHECKING:
    from typing import Coroutine, Any

_reg = re.compile(r"<color=(#\w{6})>(.*?)</color>")

TRet = TypeVar("TRet")
event_loop = asyncio.new_event_loop()
Thread(target=event_loop.run_forever, daemon=True).start()


def run_async(coro: 'Coroutine[Any, Any, TRet]') -> TRet:
    return asyncio.run_coroutine_threadsafe(coro, event_loop).result()


def colored_text(desc: str, text_box: ctk.CTkTextbox) -> ctk.CTkTextbox:
    lp = 0
    for match in _reg.finditer(desc):
        start, end = match.span()
        hex_code = match.group(1)
        content = match.group(2)

        if start > lp:
            text_box.insert("end", desc[lp:start])

        if hex_code not in text_box.tag_names():
            text_box.tag_config(hex_code, foreground=hex_code)

        text_box.insert("end", content, hex_code)
        lp = end

    if lp < len(desc):
        text_box.insert("end", desc[lp:])
    
    return text_box


def parse_args(cl_args: tuple[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dusd', action='store_false', dest="dusd", help="`dont update saved data` flag", required=False, default=True)
    return parser.parse_args(cl_args)
