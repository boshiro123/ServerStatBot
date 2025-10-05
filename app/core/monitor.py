"""
Модуль для сбора метрик системы с помощью psutil
"""
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metrics import Metric

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Класс для сбора и анализа системных метрик"""
    
    @staticmethod
    def get_cpu_metrics() -> Dict:
        """Получение метрик CPU"""
        try:
            load_avg = psutil.getloadavg()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Попытка получить температуру CPU
            cpu_temp = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Ищем температуру CPU (может быть под разными ключами)
                    for name, entries in temps.items():
                        if 'coretemp' in name.lower() or 'cpu' in name.lower():
                            if entries:
                                cpu_temp = entries[0].current
                                break
            except (AttributeError, OSError):
                pass  # sensors_temperatures может не поддерживаться на некоторых системах
            
            return {
                'cpu_load_1m': load_avg[0],
                'cpu_load_5m': load_avg[1],
                'cpu_load_15m': load_avg[2],
                'cpu_percent': cpu_percent,
                'cpu_temp': cpu_temp,
            }
        except Exception as e:
            logger.error(f"Ошибка при получении CPU метрик: {e}")
            return {}
    
    @staticmethod
    def get_memory_metrics() -> Dict:
        """Получение метрик оперативной памяти"""
        try:
            mem = psutil.virtual_memory()
            return {
                'ram_used': mem.used,
                'ram_total': mem.total,
                'ram_percent': mem.percent,
            }
        except Exception as e:
            logger.error(f"Ошибка при получении RAM метрик: {e}")
            return {}
    
    @staticmethod
    def get_disk_metrics() -> Dict:
        """Получение метрик диска"""
        try:
            disk = psutil.disk_usage('/')
            return {
                'disk_used': disk.used,
                'disk_total': disk.total,
                'disk_percent': disk.percent,
            }
        except Exception as e:
            logger.error(f"Ошибка при получении Disk метрик: {e}")
            return {}
    
    @staticmethod
    def get_network_metrics() -> Dict:
        """Получение метрик сети"""
        try:
            net = psutil.net_io_counters()
            return {
                'net_sent': net.bytes_sent,
                'net_recv': net.bytes_recv,
            }
        except Exception as e:
            logger.error(f"Ошибка при получении Network метрик: {e}")
            return {}
    
    @staticmethod
    def get_process_metrics() -> Dict:
        """Получение информации о процессах"""
        try:
            process_count = len(psutil.pids())
            return {
                'process_count': process_count,
            }
        except Exception as e:
            logger.error(f"Ошибка при получении метрик процессов: {e}")
            return {}
    
    @staticmethod
    def get_uptime() -> timedelta:
        """Получение времени работы системы"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            return datetime.now() - boot_time
        except Exception as e:
            logger.error(f"Ошибка при получении uptime: {e}")
            return timedelta(0)
    
    @staticmethod
    def get_top_processes(by: str = 'cpu', limit: int = 5) -> List[Dict]:
        """
        Получение топ процессов
        
        Args:
            by: 'cpu' или 'memory'
            limit: количество процессов
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Сортируем
            sort_key = 'cpu_percent' if by == 'cpu' else 'memory_percent'
            processes.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
            
            return processes[:limit]
        except Exception as e:
            logger.error(f"Ошибка при получении топ процессов: {e}")
            return []
    
    @classmethod
    def collect_all_metrics(cls) -> Dict:
        """Сбор всех метрик системы"""
        metrics = {}
        metrics.update(cls.get_cpu_metrics())
        metrics.update(cls.get_memory_metrics())
        metrics.update(cls.get_disk_metrics())
        metrics.update(cls.get_network_metrics())
        metrics.update(cls.get_process_metrics())
        
        return metrics
    
    @classmethod
    async def save_metrics(cls, session: AsyncSession) -> Optional[Metric]:
        """Сохранение метрик в базу данных"""
        try:
            metrics = cls.collect_all_metrics()
            
            metric = Metric(**metrics)
            session.add(metric)
            await session.commit()
            await session.refresh(metric)
            
            logger.debug(f"Метрики сохранены: {metric}")
            return metric
        except Exception as e:
            logger.error(f"Ошибка при сохранении метрик: {e}")
            await session.rollback()
            return None
    
    @staticmethod
    async def get_metrics_for_period(
        session: AsyncSession,
        hours: int = 24
    ) -> List[Metric]:
        """Получение метрик за указанный период"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            stmt = select(Metric).where(
                Metric.timestamp >= start_time
            ).order_by(Metric.timestamp)
            
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            
            return list(metrics)
        except Exception as e:
            logger.error(f"Ошибка при получении метрик из БД: {e}")
            return []
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Форматирование байтов в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    @staticmethod
    def format_uptime(uptime: timedelta) -> str:
        """Форматирование времени работы"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}д")
        if hours > 0:
            parts.append(f"{hours}ч")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}м")
        
        return ' '.join(parts)

