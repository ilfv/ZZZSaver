from io import BytesIO
from copy import deepcopy
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from lib.data_classes import GetImagesReturnStruct, GDeadlyAssaultImgsStruct


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]
    
    return wrapper


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


def gdeadlyassault2pil_image(data: 'GDeadlyAssaultImgsStruct', 
                             convert2rgba: bool = True) -> 'GDeadlyAssaultImgsStruct':
    for i in range(3):
        imgres2pil_images(data.challenges[i], False, convert2rgba)
    
    data.avatar_icon = Image.open(BytesIO(data.avatar_icon))
    data.avatar_icon = data.avatar_icon.convert("RGBA") if convert2rgba else data.avatar_icon

    return data
