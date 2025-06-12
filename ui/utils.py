import asyncio
from io import BytesIO
from threading import Thread
from typing import TYPE_CHECKING, TypeVar

from PIL import Image, ImageTk

if TYPE_CHECKING:
    from typing import Coroutine, Any


TRet = TypeVar("TRet")
event_loop = asyncio.new_event_loop()
Thread(target=event_loop.run_forever, daemon=True).start()


def bytes2pil_tk_image(data: bytes, resize: tuple[int, int] | None = None):
    img = Image.open(BytesIO(data))
    if resize:
        img = img.resize(resize)
    
    return ImageTk.PhotoImage(img)


def run_async(coro: 'Coroutine[Any, Any, TRet]') -> TRet:
    return asyncio.run_coroutine_threadsafe(coro, event_loop).result()
