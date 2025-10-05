"""
Модели базы данных для хранения метрик и настроек пользователей
"""
from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Metric(Base):
    """Модель для хранения метрик системы"""
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # CPU метрики
    cpu_load_1m = Column(Float, nullable=True)
    cpu_load_5m = Column(Float, nullable=True)
    cpu_load_15m = Column(Float, nullable=True)
    cpu_percent = Column(Float, nullable=True)
    cpu_temp = Column(Float, nullable=True)  # Температура CPU (если доступна)
    
    # RAM метрики
    ram_used = Column(BigInteger, nullable=True)  # в байтах
    ram_total = Column(BigInteger, nullable=True)  # в байтах
    ram_percent = Column(Float, nullable=True)
    
    # Disk метрики
    disk_used = Column(BigInteger, nullable=True)  # в байтах
    disk_total = Column(BigInteger, nullable=True)  # в байтах
    disk_percent = Column(Float, nullable=True)
    
    # Network метрики
    net_sent = Column(BigInteger, nullable=True)  # всего отправлено байт
    net_recv = Column(BigInteger, nullable=True)  # всего получено байт
    
    # Процессы
    process_count = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Metric(id={self.id}, timestamp={self.timestamp}, cpu={self.cpu_percent}%)>"


class UserSettings(Base):
    """Модель для хранения настроек пользователей"""
    __tablename__ = 'user_settings'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    
    # Настройки автоотправки
    auto_report_enabled = Column(Boolean, default=False)
    report_interval = Column(Integer, default=60)  # в минутах
    last_report_time = Column(DateTime, nullable=True)
    
    # Настройки уведомлений
    alerts_enabled = Column(Boolean, default=True)
    
    # Системная информация
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, auto_report={self.auto_report_enabled})>"

