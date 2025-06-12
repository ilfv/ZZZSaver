from aiogram import F, Bot, Router
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery

from lib.api import Api
from lib.save_data import SavedData

from tgbot.buttons import Buttons
from tgbot.utils import generate_image, btext_from_challenges

router = Router(name=__name__)

class Commands:

    @router.message(Command("start"))
    async def start(message: Message):
        if message.chat.type != "private":
            return
        
        await message.reply("👋", reply_markup=Buttons.start_buttons())
    
    @router.message(or_f(F.text.lower().endswith("текущий сезон"), F.text.lower().endswith("прошедший сезон")))
    async def get_season(message: Message, bot: Bot):
        season = 1 if message.text.lower().endswith("текущий сезон") else 2
        data = await Api().get_deadlyassault_info(season=season)
        img = await generate_image(data)

        await bot.send_photo(message.chat.id, img, reply_markup=Buttons.gbuffs_buttons(data.zone_id))
    
    @router.message(F.text == "📶Сохраненная информация")
    async def menu(message: Message, bot: Bot):
        await bot.send_message(message.chat.id, "⬇️", reply_markup=Buttons.menu_buttons())
    
    @router.callback_query(F.data.startswith("menuoff"))
    async def menu_offset(data: CallbackQuery):
        await data.message.edit_reply_markup(reply_markup=Buttons.menu_buttons(int(data.data.split(":")[1])))
    
    @router.callback_query(F.data.startswith("gmenu"))
    async def gf_save(data: CallbackQuery, bot: Bot):
        rid = int(data.data.split(":")[1])
        sdata = SavedData().get_by_id(rid)
        img = await generate_image(sdata)
        
        await data.message.reply_photo(img, reply_markup=Buttons.gbuffs_buttons(sdata.zone_id))
    
    @router.callback_query(F.data.startswith("gbuffs"))
    async def gbuffs_handle(data: CallbackQuery):
        zone_id = int(data.data.split(":")[1])
        sdata = SavedData().get_by_id(zone_id)

        await data.message.reply(btext_from_challenges(sdata.list))
