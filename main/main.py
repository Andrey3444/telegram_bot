import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram import types

from handlers import router
from data import create_table, responses_table, bot


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_router(router)
    # Запускаем создание таблицы базы данных
    await create_table()
    await responses_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())