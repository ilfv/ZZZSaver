from lib.save_data import SavedData

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


class Buttons:
    @staticmethod
    def start_buttons() -> ReplyKeyboardMarkup:
        keyb = []
        for text in ["📶Сохраненная информация", "Текущий сезон", "⌛Прошедший сезон"]:
            keyb.append([KeyboardButton(text=text)])
        
        return ReplyKeyboardMarkup(keyboard=keyb)
    
    @staticmethod
    def menu_buttons(offset: int = 0) -> InlineKeyboardMarkup:
        keyboard = []
        data = SavedData()[offset:offset + 10]
        for i in range(len(data)):
            deadly = data[i]
            text = deadly.start_time.to_datetime().strftime("%d.%m.%Y") + ' - ' + deadly.end_time.to_datetime().strftime("%d.%m.%Y")
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"gmenu:{deadly.zone_id}")])
        
        kb = []
        
        if len(data) == 10:
            if offset != 0:
                kb.append(InlineKeyboardButton(text="⬅️", callback_data=f"menuoff:{offset - 10}"))
            if SavedData()[offset + 10:]:
                kb.append(InlineKeyboardButton(text='➡️', callback_data=f"menuoff:{offset + 10}"))

        keyboard.append(kb)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def gbuffs_buttons(zone_id: int) -> InlineKeyboardMarkup:
        kb = [[InlineKeyboardButton(text="Buff", callback_data=f"gbuffs:{zone_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=kb)
