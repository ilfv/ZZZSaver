import re
from io import BytesIO
from typing import TYPE_CHECKING

from aiogram.types import BufferedInputFile
from PIL import Image

from lib.api import Api
from lib.image import ImageGen
from lib.utils import gdeadlyassault2pil_image

if TYPE_CHECKING:
    from lib.data_classes import DeadlyAssaultStruct, ChallengeResultStruct

_reg = re.compile(r"</?color(?:=#[0-9a-fA-F]{6})?>")


async def generate_image(data: 'DeadlyAssaultStruct',
                         return_type: BufferedInputFile | bytes | Image.Image = BufferedInputFile) -> bytes | Image.Image | BufferedInputFile:
    icons = gdeadlyassault2pil_image(await Api().get_deadlyassault_imgs(data))

    img = ImageGen().generate(data, icons)

    if return_type is Image.Image:
        return img

    buff = BytesIO()
    img.save(buff, "png")
    buff.seek(0)
    bdata = buff.read()

    if return_type is bytes:
        return bdata
    
    return BufferedInputFile(bdata, "gen.png")

def btext_from_challenges(lst: 'list[ChallengeResultStruct]') -> str:
    text = "Бафы:\n"
    for i in range(3):
        text += f"Забег №{i + 1}\n"
        for buff in lst[i].buffer:
            text += f"{buff.name}\n{_reg.sub('', buff.desc)}\n"
        text += '\n'

    return text.replace("\\n", "\n")
