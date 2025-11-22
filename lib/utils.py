from io import BytesIO
from copy import deepcopy
from typing import TYPE_CHECKING
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

from lib.data_classes import SDImgMonsterStruct

if TYPE_CHECKING:
    from lib.data_classes import (ChallengeGIStruct, 
                                  GDeadlyAssaultImgsStruct, 
                                  SDImagesStruct)


def bytes2pil(data: bytes, convert2rgba: bool) -> Image.Image:
    img = Image.open(BytesIO(data))
    if convert2rgba:
        img = img.convert("RGBA")
    
    return img


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]
    
    return wrapper


def imgres2pil_images(data: 'ChallengeGIStruct', 
                      create_copy: bool = True, 
                      convert2rgba: bool = True) -> 'ChallengeGIStruct':
    handle = partial(bytes2pil, convert2rgba=convert2rgba)
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


def gdeadlyassault2pil_image(data: 'GDeadlyAssaultImgsStruct', 
                             convert2rgba: bool = True) -> 'GDeadlyAssaultImgsStruct':
    for i in range(3):
        imgres2pil_images(data.challenges[i], False, convert2rgba)
    
    data.avatar_icon = Image.open(BytesIO(data.avatar_icon))
    data.avatar_icon = data.avatar_icon.convert("RGBA") if convert2rgba else data.avatar_icon

    return data


def sdimgs2pil(data: 'SDImagesStruct', create_copy: bool = False, convert2rgba: bool = True) -> 'SDImagesStruct':
    handle = partial(bytes2pil, convert2rgba=convert2rgba)
    if create_copy:
        data = deepcopy(data)

    def convert(args):  #args -> out_data[dict], key[int]
        odata, key = args
        tm = odata[key]

        if isinstance(tm, SDImgMonsterStruct):
            for field_name in tm.__pydantic_fields__.keys():
                setattr(tm, field_name, handle(getattr(tm, field_name)))
        else:
            odata[key] = handle(tm)

    tpe_data = []
    for dct in (data.avatars, data.monsters, data.buddys):
        for key in dct:
            tpe_data.append((dct, key))

    with ThreadPoolExecutor() as executor:
        [*executor.map(convert, tpe_data)]      #force run executor

    return data
