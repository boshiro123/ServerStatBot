"""
Главный модуль Telegram бота
"""
import os
import sys
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.db import init_db
from app.core.scheduler import init_scheduler, start_scheduler, stop_scheduler
from app.bot.handlers import commands, callbacks

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    
    # Получаем токен из переменных окружения
    bot_token = os.getenv('TELEGRAM_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_TOKEN не установлен в переменных окружения!")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)
    
    try:
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        await init_db()
        
        # Инициализация и запуск планировщика
        logger.info("Инициализация планировщика...")
        init_scheduler(bot)
        start_scheduler()
        
        # Запуск бота
        logger.info("Бот запущен и готов к работе!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        # Остановка планировщика
        stop_scheduler()
        # Закрытие бота
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

