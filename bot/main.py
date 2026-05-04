"""Точка входа — запуск бота апскейлера"""
import asyncio
import logging
import os
import sys
import time

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
# httpx и gradio_client крайне болтливы — приглушаем
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("gradio_client").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# флаг-файл для crash recovery (в /tmp/upscaler — есть как volume в compose)
CRASH_FLAG_DIR = "/tmp/upscaler"
CRASH_FLAG = os.path.join(CRASH_FLAG_DIR, ".crash_flag")


async def main() -> None:
    """Инициализация и запуск бота"""
    # подключаемся к Local Bot API если указан URL
    session = None
    api_url = settings.bot_api_url
    if api_url != "https://api.telegram.org":
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(api_url, is_local=True),
            timeout=600  # 10 минут на запрос (большие фото)
        )
        logger.info(f"Local Bot API: {api_url}")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен!)
    from bot.handlers import start, admin
    from bot.handlers import restore, settings as settings_handler, queue

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(settings_handler.router)
    dp.include_router(queue.router)
    dp.include_router(restore.router)  # последний — ловит фото

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    async def _background_cleanup() -> None:
        """Фоновая задача: очистка памяти и /tmp каждые 5 минут"""
        import glob
        from bot.middlewares.rate_limit import cleanup_stale_entries
        from bot.handlers.restore import cleanup_pending
        while True:
            await asyncio.sleep(300)  # 5 минут
            # чистим протухшие записи rate limit
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: удалено %d записей rate limit", removed)
            # чистим устаревшие pending-сессии апскейла (>10 мин)
            stale_pending = cleanup_pending()
            if stale_pending:
                logger.info("Фоновая очистка: удалено %d pending-сессий", stale_pending)
            # чистим старые файлы /tmp/upscaler (старше 10 минут)
            now = time.time()
            cutoff = now - 10 * 60
            cleaned = 0
            for f in glob.glob("/tmp/upscaler/**/*", recursive=True):
                try:
                    # пропускаем скрытые файлы (начинающиеся с точки):
                    # это .crash_flag и подобные служебные маркеры
                    if os.path.basename(f).startswith("."):
                        continue
                    if os.path.isfile(f) and os.path.getmtime(f) < cutoff:
                        os.remove(f)
                        cleaned += 1
                except OSError:
                    pass
            if cleaned:
                logger.info("Фоновая очистка: удалено %d временных файлов из /tmp/upscaler", cleaned)
            # чистим файлы Local Bot API (старше 1 часа)
            bot_api_cutoff = now - 60 * 60
            bot_api_cleaned = 0
            for f in glob.glob("/var/lib/telegram-bot-api/**/*", recursive=True):
                try:
                    if os.path.isfile(f) and os.path.getmtime(f) < bot_api_cutoff:
                        os.remove(f)
                        bot_api_cleaned += 1
                except OSError:
                    pass
            if bot_api_cleaned:
                logger.info("Фоновая очистка: удалено %d файлов Local Bot API", bot_api_cleaned)

    @dp.startup()
    async def on_startup() -> None:
        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # проверяем crash recovery
        if os.path.exists(CRASH_FLAG):
            logger.warning("Обнаружен crash-flag — предыдущий запуск завершился аварийно")
            os.remove(CRASH_FLAG)

        # ставим crash-flag
        os.makedirs(CRASH_FLAG_DIR, exist_ok=True)
        with open(CRASH_FLAG, "w") as f:
            f.write("running")

        logger.warning(
            "Бот стартовал. При первом фото возможен cold-start HF Space (до 60 сек)."
        )

        # запускаем воркер очереди реставрации
        from bot.services.queue_manager import queue_manager
        asyncio.create_task(queue_manager.worker(bot))
        logger.info("QueueManager worker запущен")

        # запускаем фоновую очистку
        asyncio.create_task(_background_cleanup())
        logger.info("Фоновая очистка запущена (интервал 5 мин)")

        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        if os.path.exists(CRASH_FLAG):
            os.remove(CRASH_FLAG)
        logger.info("Бот остановлен")

    # запускаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
