"""
Модуль для построения графиков метрик с помощью matplotlib
"""
import io
import logging
from datetime import datetime
from typing import List, Optional
import matplotlib
matplotlib.use('Agg')  # Использование non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure

from app.models.metrics import Metric

logger = logging.getLogger(__name__)

# Настройка стиля графиков
plt.style.use('seaborn-v0_8-darkgrid')


class ChartGenerator:
    """Класс для генерации графиков метрик"""
    
    @staticmethod
    def _setup_common_style(ax, title: str, ylabel: str):
        """Общие настройки стиля для всех графиков"""
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_xlabel('Время', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Форматирование оси времени
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    @staticmethod
    def create_cpu_chart(metrics: List[Metric]) -> Optional[bytes]:
        """Создание графика CPU"""
        if not metrics:
            return None
        
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            timestamps = [m.timestamp for m in metrics]
            
            # График CPU Usage
            cpu_percents = [m.cpu_percent for m in metrics if m.cpu_percent is not None]
            if cpu_percents:
                ax1.plot(timestamps[:len(cpu_percents)], cpu_percents, 
                        label='CPU Usage', color='#e74c3c', linewidth=2, marker='o', markersize=3)
                ax1.axhline(y=90, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='Порог 90%')
                ax1.fill_between(timestamps[:len(cpu_percents)], cpu_percents, alpha=0.3, color='#e74c3c')
                ChartGenerator._setup_common_style(ax1, '🖥 CPU Usage (%)', 'Использование (%)')
                ax1.set_ylim(0, 100)
                ax1.legend(loc='upper left')
            
            # График Load Average
            load_1m = [m.cpu_load_1m for m in metrics if m.cpu_load_1m is not None]
            load_5m = [m.cpu_load_5m for m in metrics if m.cpu_load_5m is not None]
            load_15m = [m.cpu_load_15m for m in metrics if m.cpu_load_15m is not None]
            
            if load_1m:
                ax2.plot(timestamps[:len(load_1m)], load_1m, label='1 min', color='#3498db', linewidth=2, marker='o', markersize=2)
            if load_5m:
                ax2.plot(timestamps[:len(load_5m)], load_5m, label='5 min', color='#2ecc71', linewidth=2, marker='s', markersize=2)
            if load_15m:
                ax2.plot(timestamps[:len(load_15m)], load_15m, label='15 min', color='#9b59b6', linewidth=2, marker='^', markersize=2)
            
            ChartGenerator._setup_common_style(ax2, '📊 CPU Load Average', 'Load')
            ax2.legend(loc='upper left')
            
            plt.tight_layout()
            
            # Сохранение в буфер
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Ошибка при создании графика CPU: {e}")
            return None
    
    @staticmethod
    def create_memory_chart(metrics: List[Metric]) -> Optional[bytes]:
        """Создание графика памяти"""
        if not metrics:
            return None
        
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            timestamps = [m.timestamp for m in metrics]
            ram_percents = [m.ram_percent for m in metrics if m.ram_percent is not None]
            
            if ram_percents:
                ax.plot(timestamps[:len(ram_percents)], ram_percents, 
                       label='RAM Usage', color='#2ecc71', linewidth=2.5, marker='o', markersize=3)
                ax.axhline(y=90, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='Порог 90%')
                ax.fill_between(timestamps[:len(ram_percents)], ram_percents, alpha=0.3, color='#2ecc71')
                
                ChartGenerator._setup_common_style(ax, '🧠 RAM Usage', 'Использование (%)')
                ax.set_ylim(0, 100)
                ax.legend(loc='upper left')
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Ошибка при создании графика RAM: {e}")
            return None
    
    @staticmethod
    def create_disk_chart(metrics: List[Metric]) -> Optional[bytes]:
        """Создание графика диска"""
        if not metrics:
            return None
        
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            timestamps = [m.timestamp for m in metrics]
            disk_percents = [m.disk_percent for m in metrics if m.disk_percent is not None]
            
            if disk_percents:
                ax.plot(timestamps[:len(disk_percents)], disk_percents, 
                       label='Disk Usage', color='#f39c12', linewidth=2.5, marker='s', markersize=3)
                ax.axhline(y=90, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Порог 90%')
                ax.fill_between(timestamps[:len(disk_percents)], disk_percents, alpha=0.3, color='#f39c12')
                
                ChartGenerator._setup_common_style(ax, '💾 Disk Usage', 'Использование (%)')
                ax.set_ylim(0, 100)
                ax.legend(loc='upper left')
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Ошибка при создании графика Disk: {e}")
            return None
    
    @staticmethod
    def create_network_chart(metrics: List[Metric]) -> Optional[bytes]:
        """Создание графика сети"""
        if not metrics:
            return None
        
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            timestamps = [m.timestamp for m in metrics]
            
            # Вычисляем разницу для получения скорости
            net_sent_mb = []
            net_recv_mb = []
            
            for i in range(1, len(metrics)):
                if metrics[i].net_sent and metrics[i-1].net_sent:
                    sent_diff = (metrics[i].net_sent - metrics[i-1].net_sent) / (1024 * 1024)  # MB
                    net_sent_mb.append(sent_diff if sent_diff >= 0 else 0)
                
                if metrics[i].net_recv and metrics[i-1].net_recv:
                    recv_diff = (metrics[i].net_recv - metrics[i-1].net_recv) / (1024 * 1024)  # MB
                    net_recv_mb.append(recv_diff if recv_diff >= 0 else 0)
            
            if net_sent_mb:
                ax.plot(timestamps[1:len(net_sent_mb)+1], net_sent_mb, 
                       label='Отправлено', color='#e74c3c', linewidth=2, marker='^', markersize=3)
            if net_recv_mb:
                ax.plot(timestamps[1:len(net_recv_mb)+1], net_recv_mb, 
                       label='Получено', color='#3498db', linewidth=2, marker='v', markersize=3)
            
            ChartGenerator._setup_common_style(ax, '🌐 Network Traffic', 'Скорость (MB/период)')
            ax.legend(loc='upper left')
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Ошибка при создании графика Network: {e}")
            return None
    
    @classmethod
    def create_all_charts(cls, metrics: List[Metric]) -> dict:
        """Создание всех графиков"""
        return {
            'cpu': cls.create_cpu_chart(metrics),
            'memory': cls.create_memory_chart(metrics),
            'disk': cls.create_disk_chart(metrics),
            'network': cls.create_network_chart(metrics),
        }

