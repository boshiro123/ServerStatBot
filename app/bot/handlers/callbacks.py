"""
Обработчики callback-запросов
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from datetime import datetime, timedelta

from app.core.db import async_session_maker
from app.core.monitor import SystemMonitor
from app.core.charts import ChartGenerator

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("graph_"))
async def callback_graph(callback: CallbackQuery):
    """Обработчик callback для графиков"""
    try:
        # Извлекаем период из callback_data
        hours = int(callback.data.split("_")[1])
        
        await callback.answer()
        await callback.message.edit_text(
            f"⏳ Генерирую графики за {hours}ч... Пожалуйста, подождите."
        )
        
        # Получаем метрики из БД
        async with async_session_maker() as session:
            metrics = await SystemMonitor.get_metrics_for_period(session, hours=hours)
        
        if not metrics:
            await callback.message.edit_text(
                "❌ Нет данных за выбранный период.\n"
                "Метрики ещё не накоплены или база данных пуста."
            )
            return
        
        # Генерируем графики
        charts = ChartGenerator.create_all_charts(metrics)
        
        period_text = f"{hours}ч" if hours < 24 else f"{hours // 24}д"
        
        # Отправляем графики
        for chart_name, chart_data in charts.items():
            if chart_data:
                chart_file = BufferedInputFile(
                    chart_data,
                    filename=f"{chart_name}_{period_text}.png"
                )
                
                caption_map = {
                    'cpu': f"🖥 CPU метрики за {period_text}",
                    'memory': f"🧠 RAM метрики за {period_text}",
                    'disk': f"💾 Disk метрики за {period_text}",
                    'network': f"🌐 Network метрики за {period_text}",
                }
                
                await callback.message.answer_photo(
                    photo=chart_file,
                    caption=caption_map.get(chart_name, f"График за {period_text}")
                )
        
        await callback.message.edit_text(
            f"✅ Графики за {period_text} успешно отправлены!"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в callback_graph: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при генерации графиков"
        )


@router.callback_query(F.data.startswith("history_"))
async def callback_history(callback: CallbackQuery):
    """Обработчик callback для истории"""
    try:
        # Извлекаем период из callback_data
        hours = int(callback.data.split("_")[1])
        
        await callback.answer()
        await callback.message.edit_text(
            f"⏳ Загружаю историю за {hours}ч..."
        )
        
        # Получаем метрики из БД
        async with async_session_maker() as session:
            metrics = await SystemMonitor.get_metrics_for_period(session, hours=hours)
        
        if not metrics:
            await callback.message.edit_text(
                "❌ Нет данных за выбранный период."
            )
            return
        
        # Анализируем метрики
        cpu_values = [m.cpu_percent for m in metrics if m.cpu_percent is not None]
        ram_values = [m.ram_percent for m in metrics if m.ram_percent is not None]
        disk_values = [m.disk_percent for m in metrics if m.disk_percent is not None]
        
        period_text = f"{hours}ч" if hours < 24 else f"{hours // 24}д"
        
        text = f"📊 <b>История метрик за {period_text}</b>\n\n"
        text += f"📅 Период: {metrics[0].timestamp.strftime('%d.%m %H:%M')} - "
        text += f"{metrics[-1].timestamp.strftime('%d.%m %H:%M')}\n"
        text += f"📈 Записей: {len(metrics)}\n\n"
        
        # CPU статистика
        if cpu_values:
            text += "🖥 <b>CPU:</b>\n"
            text += f"  • Среднее: {sum(cpu_values)/len(cpu_values):.1f}%\n"
            text += f"  • Минимум: {min(cpu_values):.1f}%\n"
            text += f"  • Максимум: {max(cpu_values):.1f}%\n"
            
            # Подсчитываем случаи превышения порога
            high_cpu = sum(1 for v in cpu_values if v > 80)
            if high_cpu:
                text += f"  • ⚠️ Высокая нагрузка (>80%): {high_cpu} раз\n"
        
        # RAM статистика
        if ram_values:
            text += "\n🧠 <b>RAM:</b>\n"
            text += f"  • Среднее: {sum(ram_values)/len(ram_values):.1f}%\n"
            text += f"  • Минимум: {min(ram_values):.1f}%\n"
            text += f"  • Максимум: {max(ram_values):.1f}%\n"
            
            high_ram = sum(1 for v in ram_values if v > 80)
            if high_ram:
                text += f"  • ⚠️ Высокое использование (>80%): {high_ram} раз\n"
        
        # Disk статистика
        if disk_values:
            text += "\n💾 <b>Disk:</b>\n"
            text += f"  • Среднее: {sum(disk_values)/len(disk_values):.1f}%\n"
            text += f"  • Минимум: {min(disk_values):.1f}%\n"
            text += f"  • Максимум: {max(disk_values):.1f}%\n"
        
        # Network статистика
        if len(metrics) > 1:
            first_sent = metrics[0].net_sent or 0
            last_sent = metrics[-1].net_sent or 0
            first_recv = metrics[0].net_recv or 0
            last_recv = metrics[-1].net_recv or 0
            
            total_sent = last_sent - first_sent
            total_recv = last_recv - first_recv
            
            text += "\n🌐 <b>Network (за период):</b>\n"
            text += f"  • Отправлено: {SystemMonitor.format_bytes(total_sent)}\n"
            text += f"  • Получено: {SystemMonitor.format_bytes(total_recv)}\n"
        
        await callback.message.edit_text(text)
        
    except Exception as e:
        logger.error(f"Ошибка в callback_history: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке истории"
        )

