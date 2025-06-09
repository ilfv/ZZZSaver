import asyncio
from io import BytesIO
from copy import deepcopy
from threading import Thread
from typing import TYPE_CHECKING, TypeVar

from PIL import Image, ImageTk

if TYPE_CHECKING:
    from typing import Coroutine, Any

    from lib.data_classes import GetImagesReturnStruct


TRet = TypeVar("TRet")
event_loop = asyncio.new_event_loop()
Thread(target=event_loop.run_forever, daemon=True).start()


def bytes2pil_tk_image(data: bytes, resize: tuple[int, int] | None = None):
    img = Image.open(BytesIO(data))
    if resize:
        img = img.resize(resize)
    
    return ImageTk.PhotoImage(img)

def imgres2pil_images(data: 'GetImagesReturnStruct', 
                      create_copy: bool = True, 
                      convert2rgba: bool = True) -> 'GetImagesReturnStruct':
    def handle(data):
        img = Image.open(BytesIO(data))
        if convert2rgba:
            img = img.convert("RGBA")
        
        return img

    if create_copy:
        data = deepcopy(data)

    for i in range(len(data.avatars)):
        data.avatars[i] = handle(data.avatars[i])
    
    for i in range(len(data.buff)):
        data.buff[i] = handle(data.buff[i])

    for i in range(len(data.boss)):
        for attr in ["icon", "race_icon", "bg_icon"]:
            setattr(data.boss[i], attr, handle(getattr(data.boss[i], attr)))
    
    data.buddy = handle(data.buddy)
    
    return data


def run_async(coro: 'Coroutine[Any, Any, TRet]') -> TRet:
    return asyncio.run_coroutine_threadsafe(coro, event_loop).result()
