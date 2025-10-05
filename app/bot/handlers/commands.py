"""
Обработчики команд бота
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.core.db import async_session_maker
from app.core.monitor import SystemMonitor
from app.models.metrics import UserSettings
from app.utils.helpers import get_or_create_user_settings
from app.bot.keyboards.inline import get_period_keyboard, get_history_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    async with async_session_maker() as session:
        await get_or_create_user_settings(
            session,
            message.from_user.id,
            message.from_user.username
        )
    
    await message.answer(
        "👋 <b>Добро пожаловать в Server Monitor Bot!</b>\n\n"
        "Я помогу вам отслеживать состояние вашего сервера.\n\n"
        "Используйте /help для просмотра доступных команд."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/status - Текущие показатели сервера\n"
        "/graph - Графики метрик (выбор периода)\n"
        "/history - Текстовый отчёт за период\n"
        "/top - Топ процессов по CPU и RAM\n"
        "/setinterval [минуты] - Установить автоотправку\n"
        "/stop - Остановить автоотправку\n"
        "/settings - Ваши текущие настройки\n"
        "/help - Эта справка"
    )
    await message.answer(help_text)


@router.message(Command("status"))
async def cmd_status(message: Message):
    """Обработчик команды /status"""
    try:
        # Получаем текущие метрики
        cpu = SystemMonitor.get_cpu_metrics()
        memory = SystemMonitor.get_memory_metrics()
        disk = SystemMonitor.get_disk_metrics()
        network = SystemMonitor.get_network_metrics()
        uptime = SystemMonitor.get_uptime()
        processes = SystemMonitor.get_process_metrics()
        
        # Форматируем сообщение
        status_text = "📊 <b>Текущее состояние сервера</b>\n\n"
        
        # CPU
        status_text += f"🖥 <b>CPU:</b>\n"
        status_text += f"  • Использование: {cpu.get('cpu_percent', 0):.1f}%\n"
        status_text += f"  • Load Avg: {cpu.get('cpu_load_1m', 0):.2f} / "
        status_text += f"{cpu.get('cpu_load_5m', 0):.2f} / {cpu.get('cpu_load_15m', 0):.2f}\n"
        
        if cpu.get('cpu_temp'):
            status_text += f"  • Температура: {cpu.get('cpu_temp'):.1f}°C\n"
        
        # RAM
        ram_used = memory.get('ram_used', 0)
        ram_total = memory.get('ram_total', 1)
        ram_percent = memory.get('ram_percent', 0)
        status_text += f"\n🧠 <b>RAM:</b>\n"
        status_text += f"  • {SystemMonitor.format_bytes(ram_used)} / "
        status_text += f"{SystemMonitor.format_bytes(ram_total)} ({ram_percent:.1f}%)\n"
        
        # Disk
        disk_used = disk.get('disk_used', 0)
        disk_total = disk.get('disk_total', 1)
        disk_percent = disk.get('disk_percent', 0)
        status_text += f"\n💾 <b>Disk:</b>\n"
        status_text += f"  • {SystemMonitor.format_bytes(disk_used)} / "
        status_text += f"{SystemMonitor.format_bytes(disk_total)} ({disk_percent:.1f}%)\n"
        
        # Network
        net_sent = network.get('net_sent', 0)
        net_recv = network.get('net_recv', 0)
        status_text += f"\n🌐 <b>Network:</b>\n"
        status_text += f"  • ↑ Отправлено: {SystemMonitor.format_bytes(net_sent)}\n"
        status_text += f"  • ↓ Получено: {SystemMonitor.format_bytes(net_recv)}\n"
        
        # Uptime & Processes
        status_text += f"\n⏱ <b>Uptime:</b> {SystemMonitor.format_uptime(uptime)}\n"
        status_text += f"⚙️ <b>Процессов:</b> {processes.get('process_count', 0)}\n"
        
        await message.answer(status_text)
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_status: {e}")
        await message.answer("❌ Ошибка при получении статуса сервера")


@router.message(Command("graph"))
async def cmd_graph(message: Message):
    """Обработчик команды /graph"""
    await message.answer(
        "📈 <b>Выберите период для графиков:</b>",
        reply_markup=get_period_keyboard()
    )


@router.message(Command("history"))
async def cmd_history(message: Message):
    """Обработчик команды /history"""
    await message.answer(
        "📜 <b>Выберите период для истории:</b>",
        reply_markup=get_history_keyboard()
    )


@router.message(Command("top"))
async def cmd_top(message: Message):
    """Обработчик команды /top"""
    try:
        # Топ процессов по CPU
        top_cpu = SystemMonitor.get_top_processes(by='cpu', limit=5)
        # Топ процессов по RAM
        top_mem = SystemMonitor.get_top_processes(by='memory', limit=5)
        
        text = "📊 <b>Топ процессов</b>\n\n"
        
        text += "🔥 <b>По CPU:</b>\n"
        for i, proc in enumerate(top_cpu, 1):
            text += f"{i}. {proc.get('name', 'Unknown')[:20]} - "
            text += f"{proc.get('cpu_percent', 0):.1f}% (PID: {proc.get('pid')})\n"
        
        text += "\n💾 <b>По RAM:</b>\n"
        for i, proc in enumerate(top_mem, 1):
            text += f"{i}. {proc.get('name', 'Unknown')[:20]} - "
            text += f"{proc.get('memory_percent', 0):.1f}% (PID: {proc.get('pid')})\n"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_top: {e}")
        await message.answer("❌ Ошибка при получении списка процессов")


@router.message(Command("setinterval"))
async def cmd_setinterval(message: Message):
    """Обработчик команды /setinterval"""
    try:
        # Парсим аргументы
        args = message.text.split()
        if len(args) < 2:
            await message.answer(
                "❌ Укажите интервал в минутах.\n"
                "Пример: /setinterval 60"
            )
            return
        
        try:
            interval = int(args[1])
            if interval < 1 or interval > 1440:  # макс 24 часа
                await message.answer("❌ Интервал должен быть от 1 до 1440 минут")
                return
        except ValueError:
            await message.answer("❌ Интервал должен быть числом")
            return
        
        # Сохраняем настройки
        async with async_session_maker() as session:
            user_settings = await get_or_create_user_settings(
                session,
                message.from_user.id,
                message.from_user.username
            )
            user_settings.auto_report_enabled = True
            user_settings.report_interval = interval
            await session.commit()
        
        await message.answer(
            f"✅ Автоматическая отправка отчётов включена.\n"
            f"Интервал: {interval} минут"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_setinterval: {e}")
        await message.answer("❌ Ошибка при настройке интервала")


@router.message(Command("stop"))
async def cmd_stop(message: Message):
    """Обработчик команды /stop"""
    try:
        async with async_session_maker() as session:
            user_settings = await get_or_create_user_settings(
                session,
                message.from_user.id,
                message.from_user.username
            )
            user_settings.auto_report_enabled = False
            await session.commit()
        
        await message.answer("⏸ Автоматическая отправка отчётов остановлена")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_stop: {e}")
        await message.answer("❌ Ошибка при остановке автоотправки")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Обработчик команды /settings"""
    try:
        async with async_session_maker() as session:
            user_settings = await get_or_create_user_settings(
                session,
                message.from_user.id,
                message.from_user.username
            )
            
            text = "⚙️ <b>Ваши настройки:</b>\n\n"
            text += f"👤 User ID: {user_settings.user_id}\n"
            
            if user_settings.auto_report_enabled:
                text += f"📊 Автоотправка: ✅ включена\n"
                text += f"⏱ Интервал: {user_settings.report_interval} минут\n"
            else:
                text += f"📊 Автоотправка: ❌ отключена\n"
            
            text += f"🔔 Уведомления: {'✅' if user_settings.alerts_enabled else '❌'}\n"
            
            await message.answer(text)
            
    except Exception as e:
        logger.error(f"Ошибка в cmd_settings: {e}")
        await message.answer("❌ Ошибка при получении настроек")

