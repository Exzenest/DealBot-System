from aiogram import Dispatcher, Bot
from src.database.config import config
from baseCommands import router as baseRouter
import asyncio
import os
import inspect
from aiogram.fsm.storage.memory import MemoryStorage
print("CONFIG MODULE:", inspect.getfile(config.__class__))
print("DB NAME:", config.db.name)
print("DB EXISTS:", os.path.exists(config.db.name))

print("WORKDIR:", os.getcwd())
print("DB URL:", config.db.url)
print("DB PATH EXISTS:", os.path.exists(config.db.name))



async def main():
    bot_config = config.load_bot()

    bot = Bot(token=bot_config.token_task.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(baseRouter)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



