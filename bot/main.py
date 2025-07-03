import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from database.db import init_db
from bot.handlers.order import order_router
import sys

async def on_startup():
    await init_db()
    print("База данных инициализирована!")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(order_router)

    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Запуск Telegram-бота...")
        print(f"[INFO] BOT_TOKEN: {BOT_TOKEN}")
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] Произошла ошибка при запуске бота: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
