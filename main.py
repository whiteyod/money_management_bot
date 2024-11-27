import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage 

from config_reader import config
from handlers import commands, buttons, categories_handling, dashboard_button



# Configure logging and storage
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()


# Enable polling
async def main():
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode='HTML')
    dp = Dispatcher(storage=storage)
    dp.include_routers(commands.router, buttons.router, categories_handling.router, dashboard_button.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())