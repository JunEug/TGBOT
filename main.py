import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters import Command
from config import BOT_TOKEN
from handlers.currency_handlers import router
from database import create_tables


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

dp = Dispatcher()

dp.include_router(router)

async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    create_tables()
    asyncio.run(main())
