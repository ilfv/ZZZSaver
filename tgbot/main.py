import sys; sys.path.append('.')
import os
import asyncio

from aiogram import Bot, Dispatcher

from lib.api import Api
from lib.logger import get_logger

from commands import router as c_router

_log = get_logger(__file__, "Main")


class App:
    def __init__(self):
        self.dp = Dispatcher()
        self.dp.include_router(c_router)

    async def start(self):
        await Api().update_saved_data()

        bot = Bot(os.environ["BOT_TOKEN"])
        me = await bot.get_me()

        _log.info(f"succes login as {me.full_name}/@{me.username}")

        await self.dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(App().start())
