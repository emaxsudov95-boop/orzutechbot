import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from config import BOT_TOKEN, PORT
from database import init_db
from handlers import main_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Render.com uchun HTTP health check handler"""
    return web.json_response({
        "status": "online",
        "bot": "SMM BOT",
        "version": "1.0.0"
    })

async def start_web_server():
    """Render.com da Web Service sifatida uzluksiz ishlashini ta'minlovchi veb-server"""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Health server {PORT}-portda ishga tushirildi.")

async def main():
    logger.info("Bot ishga tushmoqda...")

    # Bazani tayyorlash
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(main_router)

    # Render.com portini tinglash uchun yengil serverni ishga tushirish
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Veb serverni ishga tushirishda ogohlantirish (e'tibor bermaslik mumkin): {e}")

    # Eski kutilayotgan yangilanishlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)

    # Telegram Menyu (Buyruqlar) ro'yxatini sozlash
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Asosiy menyuni ochish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
        BotCommand(command="admin", description="Admin boshqaruv paneli"),
        BotCommand(command="myid", description="Telegram ID raqamim"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Buyruqlarni o'rnatishda xatolik: {e}")

    logger.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni qabul qilmoqda!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
