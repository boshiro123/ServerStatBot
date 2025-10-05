"""
Модуль для фоновых задач и планировщика
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import BufferedInputFile

from app.core.db import async_session_maker
from app.core.monitor import SystemMonitor
from app.core.charts import ChartGenerator
from app.models.metrics import UserSettings
from app.utils.helpers import get_env_int, get_env_float

logger = logging.getLogger(__name__)

# Глобальный планировщик
scheduler: Optional[AsyncIOScheduler] = None
bot_instance: Optional[Bot] = None

# Пороги для алертов
ALERT_CPU_THRESHOLD = get_env_float('ALERT_CPU_THRESHOLD', 90.0)
ALERT_RAM_THRESHOLD = get_env_float('ALERT_RAM_THRESHOLD', 90.0)
ALERT_DISK_THRESHOLD = get_env_float('ALERT_DISK_THRESHOLD', 90.0)

# Словарь для отслеживания отправленных алертов (чтобы не спамить)
last_alerts = {
    'cpu': None,
    'ram': None,
    'disk': None,
}


async def collect_metrics_job():
    """Фоновая задача для сбора метрик"""
    try:
        async with async_session_maker() as session:
            metric = await SystemMonitor.save_metrics(session)
            if metric:
                logger.debug(f"Метрики собраны: CPU {metric.cpu_percent}%, RAM {metric.ram_percent}%")
                
                # Проверяем пороги для алертов
                await check_alerts(metric)
    except Exception as e:
        logger.error(f"Ошибка при сборе метрик: {e}")


async def check_alerts(metric):
    """Проверка порогов и отправка алертов"""
    global last_alerts
    
    if not bot_instance:
        return
    
    try:
        # Получаем всех пользователей с включёнными алертами
        async with async_session_maker() as session:
            stmt = select(UserSettings).where(UserSettings.alerts_enabled == True)
            result = await session.execute(stmt)
            users = result.scalars().all()
        
        current_time = datetime.utcnow()
        
        # Проверяем CPU
        if metric.cpu_percent and metric.cpu_percent > ALERT_CPU_THRESHOLD:
            if not last_alerts['cpu'] or (current_time - last_alerts['cpu']).seconds > 300:  # 5 минут
                for user in users:
                    try:
                        await bot_instance.send_message(
                            user.user_id,
                            f"⚠️ <b>ПРЕДУПРЕЖДЕНИЕ: Высокая нагрузка CPU!</b>\n\n"
                            f"Текущее значение: {metric.cpu_percent:.1f}%\n"
                            f"Порог: {ALERT_CPU_THRESHOLD}%"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки алерта пользователю {user.user_id}: {e}")
                
                last_alerts['cpu'] = current_time
        
        # Проверяем RAM
        if metric.ram_percent and metric.ram_percent > ALERT_RAM_THRESHOLD:
            if not last_alerts['ram'] or (current_time - last_alerts['ram']).seconds > 300:
                for user in users:
                    try:
                        await bot_instance.send_message(
                            user.user_id,
                            f"⚠️ <b>ПРЕДУПРЕЖДЕНИЕ: Высокое использование RAM!</b>\n\n"
                            f"Текущее значение: {metric.ram_percent:.1f}%\n"
                            f"Порог: {ALERT_RAM_THRESHOLD}%"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки алерта пользователю {user.user_id}: {e}")
                
                last_alerts['ram'] = current_time
        
        # Проверяем Disk
        if metric.disk_percent and metric.disk_percent > ALERT_DISK_THRESHOLD:
            if not last_alerts['disk'] or (current_time - last_alerts['disk']).seconds > 300:
                for user in users:
                    try:
                        await bot_instance.send_message(
                            user.user_id,
                            f"⚠️ <b>ПРЕДУПРЕЖДЕНИЕ: Мало места на диске!</b>\n\n"
                            f"Текущее значение: {metric.disk_percent:.1f}%\n"
                            f"Порог: {ALERT_DISK_THRESHOLD}%"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки алерта пользователю {user.user_id}: {e}")
                
                last_alerts['disk'] = current_time
    
    except Exception as e:
        logger.error(f"Ошибка при проверке алертов: {e}")


async def send_auto_reports_job():
    """Фоновая задача для автоматической отправки отчётов"""
    if not bot_instance:
        return
    
    try:
        async with async_session_maker() as session:
            # Получаем пользователей с включённой автоотправкой
            stmt = select(UserSettings).where(UserSettings.auto_report_enabled == True)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            current_time = datetime.utcnow()
            
            for user in users:
                try:
                    # Проверяем, нужно ли отправлять отчёт
                    should_send = False
                    
                    if user.last_report_time is None:
                        should_send = True
                    else:
                        time_since_last = (current_time - user.last_report_time).total_seconds() / 60
                        if time_since_last >= user.report_interval:
                            should_send = True
                    
                    if should_send:
                        # Отправляем отчёт
                        await send_report_to_user(user.user_id)
                        
                        # Обновляем время последней отправки
                        user.last_report_time = current_time
                        await session.commit()
                        
                        logger.info(f"Отправлен автоотчёт пользователю {user.user_id}")
                
                except Exception as e:
                    logger.error(f"Ошибка отправки автоотчёта пользователю {user.user_id}: {e}")
    
    except Exception as e:
        logger.error(f"Ошибка в задаче автоотчётов: {e}")


async def send_report_to_user(user_id: int):
    """Отправка отчёта пользователю"""
    if not bot_instance:
        return
    
    try:
        # Получаем текущий статус
        cpu = SystemMonitor.get_cpu_metrics()
        memory = SystemMonitor.get_memory_metrics()
        disk = SystemMonitor.get_disk_metrics()
        
        status_text = "📊 <b>Автоматический отчёт</b>\n\n"
        status_text += f"🖥 CPU: {cpu.get('cpu_percent', 0):.1f}%\n"
        status_text += f"🧠 RAM: {memory.get('ram_percent', 0):.1f}%\n"
        status_text += f"💾 Disk: {disk.get('disk_percent', 0):.1f}%\n"
        
        await bot_instance.send_message(user_id, status_text)
        
        # Отправляем график за последний час
        async with async_session_maker() as session:
            metrics = await SystemMonitor.get_metrics_for_period(session, hours=1)
        
        if metrics:
            # Отправляем только CPU график
            chart_data = ChartGenerator.create_cpu_chart(metrics)
            if chart_data:
                chart_file = BufferedInputFile(chart_data, filename="cpu_report.png")
                await bot_instance.send_photo(
                    user_id,
                    photo=chart_file,
                    caption="📈 CPU метрики за последний час"
                )
    
    except Exception as e:
        logger.error(f"Ошибка при отправке отчёта: {e}")


def init_scheduler(bot: Bot):
    """Инициализация планировщика"""
    global scheduler, bot_instance
    
    bot_instance = bot
    scheduler = AsyncIOScheduler()
    
    # Интервал сбора метрик (из .env, по умолчанию 60 секунд)
    monitor_interval = get_env_int('MONITOR_INTERVAL', 60)
    
    # Задача для сбора метрик
    scheduler.add_job(
        collect_metrics_job,
        trigger=IntervalTrigger(seconds=monitor_interval),
        id='collect_metrics',
        name='Collect system metrics',
        replace_existing=True,
    )
    
    # Задача для автоотчётов (проверяем каждую минуту)
    scheduler.add_job(
        send_auto_reports_job,
        trigger=IntervalTrigger(minutes=1),
        id='auto_reports',
        name='Send auto reports',
        replace_existing=True,
    )
    
    logger.info("Планировщик инициализирован")


def start_scheduler():
    """Запуск планировщика"""
    if scheduler and not scheduler.running:
        scheduler.start()
        logger.info("Планировщик запущен")


def stop_scheduler():
    """Остановка планировщика"""
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Планировщик остановлен")

