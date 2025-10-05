# 📁 Структура проекта Server Monitor Bot

## Общая структура

```
ServerStat/
├── 📄 README.md                    # Основная документация
├── 📄 INSTALL.md                   # Инструкция по установке
├── 📄 PROJECT_STRUCTURE.md         # Этот файл
├── 📄 requirements.txt             # Python зависимости
├── 📄 Dockerfile                   # Docker образ
├── 📄 docker-compose.yml           # Docker Compose конфигурация
├── 📄 .dockerignore                # Исключения для Docker
├── 📄 .gitignore                   # Исключения для Git
├── 📄 env.example                  # Пример конфигурации
├── 📄 Makefile                     # Команды для управления
├── 🔧 start.sh                     # Скрипт быстрого запуска
│
├── 📂 app/                         # Исходный код приложения
│   ├── __init__.py
│   │
│   ├── 📂 bot/                     # Telegram бот
│   │   ├── __init__.py
│   │   ├── main.py                 # Точка входа в приложение
│   │   │
│   │   ├── 📂 handlers/            # Обработчики событий бота
│   │   │   ├── __init__.py
│   │   │   ├── commands.py         # Обработчики команд (/start, /status, и т.д.)
│   │   │   └── callbacks.py        # Обработчики callback-кнопок
│   │   │
│   │   └── 📂 keyboards/           # Клавиатуры
│   │       ├── __init__.py
│   │       └── inline.py           # Inline-клавиатуры (кнопки выбора периода)
│   │
│   ├── 📂 core/                    # Основная бизнес-логика
│   │   ├── __init__.py
│   │   ├── monitor.py              # Сбор метрик системы (psutil)
│   │   ├── db.py                   # Работа с базой данных
│   │   ├── charts.py               # Генерация графиков (matplotlib)
│   │   └── scheduler.py            # Фоновые задачи (APScheduler)
│   │
│   ├── 📂 models/                  # Модели базы данных
│   │   ├── __init__.py
│   │   └── metrics.py              # SQLAlchemy модели (Metric, UserSettings)
│   │
│   └── 📂 utils/                   # Вспомогательные функции
│       ├── __init__.py
│       └── helpers.py              # Утилиты и helper функции
│
└── 📂 logs/                        # Логи (создаётся автоматически)
    └── bot.log
```

---

## Подробное описание модулей

### 🤖 Bot Module (`app/bot/`)

#### `main.py`

- **Назначение**: Точка входа в приложение
- **Функции**:
  - Инициализация бота и диспетчера
  - Регистрация handlers
  - Запуск планировщика
  - Инициализация БД
  - Polling обновлений

#### `handlers/commands.py`

- **Назначение**: Обработка текстовых команд
- **Команды**:
  - `/start` — Приветствие и регистрация пользователя
  - `/help` — Справка по командам
  - `/status` — Текущие метрики сервера
  - `/graph` — Вызов меню выбора периода для графиков
  - `/history` — Вызов меню выбора периода для истории
  - `/top` — Топ процессов по CPU и RAM
  - `/setinterval <минуты>` — Настройка автоотправки
  - `/stop` — Остановка автоотправки
  - `/settings` — Текущие настройки пользователя

#### `handlers/callbacks.py`

- **Назначение**: Обработка нажатий на inline-кнопки
- **Callbacks**:
  - `graph_<hours>` — Генерация и отправка графиков
  - `history_<hours>` — Формирование статистики за период

#### `keyboards/inline.py`

- **Назначение**: Inline-клавиатуры
- **Клавиатуры**:
  - `get_period_keyboard()` — Выбор периода для графиков (1ч, 6ч, 24ч, 7д)
  - `get_history_keyboard()` — Выбор периода для истории

---

### ⚙️ Core Module (`app/core/`)

#### `monitor.py`

- **Назначение**: Сбор системных метрик
- **Класс**: `SystemMonitor`
- **Методы**:
  - `get_cpu_metrics()` — CPU usage, load average, температура
  - `get_memory_metrics()` — RAM usage
  - `get_disk_metrics()` — Disk usage
  - `get_network_metrics()` — Network traffic
  - `get_process_metrics()` — Количество процессов
  - `get_uptime()` — Время работы системы
  - `get_top_processes()` — Топ процессов
  - `collect_all_metrics()` — Сбор всех метрик разом
  - `save_metrics()` — Сохранение в БД
  - `get_metrics_for_period()` — Получение из БД за период
  - `format_bytes()` — Форматирование байтов
  - `format_uptime()` — Форматирование uptime

#### `db.py`

- **Назначение**: Работа с базой данных
- **Компоненты**:
  - `engine` — Асинхронный SQLAlchemy engine
  - `async_session_maker` — Фабрика сессий
  - `init_db()` — Создание таблиц
  - `get_session()` — Получение сессии (async generator)

#### `charts.py`

- **Назначение**: Генерация графиков
- **Класс**: `ChartGenerator`
- **Методы**:
  - `create_cpu_chart()` — График CPU (usage + load avg)
  - `create_memory_chart()` — График RAM
  - `create_disk_chart()` — График Disk
  - `create_network_chart()` — График Network traffic
  - `create_all_charts()` — Все графики разом
- **Особенности**:
  - Использует matplotlib
  - Возвращает bytes (PNG)
  - Стилизованные графики с порогами

#### `scheduler.py`

- **Назначение**: Фоновые задачи и планировщик
- **Компоненты**:
  - `collect_metrics_job()` — Периодический сбор метрик
  - `check_alerts()` — Проверка порогов и отправка алертов
  - `send_auto_reports_job()` — Автоматическая отправка отчётов
  - `send_report_to_user()` — Отправка отчёта конкретному пользователю
  - `init_scheduler()` — Инициализация APScheduler
  - `start_scheduler()` / `stop_scheduler()` — Управление
- **Задачи**:
  - Сбор метрик: каждые N секунд (MONITOR_INTERVAL)
  - Проверка автоотчётов: каждую минуту
  - Алерты: при превышении порогов (не чаще раза в 5 минут)

---

### 🗄️ Models Module (`app/models/`)

#### `metrics.py`

- **Назначение**: SQLAlchemy модели

##### Модель `Metric`

Хранит метрики системы:

- `id` — PK
- `timestamp` — Время сбора
- `cpu_load_1m, cpu_load_5m, cpu_load_15m` — Load average
- `cpu_percent` — CPU usage в процентах
- `cpu_temp` — Температура CPU (опционально)
- `ram_used, ram_total, ram_percent` — RAM метрики
- `disk_used, disk_total, disk_percent` — Disk метрики
- `net_sent, net_recv` — Network cumulative bytes
- `process_count` — Количество процессов

##### Модель `UserSettings`

Хранит настройки пользователей:

- `user_id` — Telegram user_id (PK)
- `username` — Telegram username
- `auto_report_enabled` — Включена ли автоотправка
- `report_interval` — Интервал в минутах
- `last_report_time` — Время последней отправки
- `alerts_enabled` — Включены ли алерты
- `created_at, updated_at` — Системные поля

---

### 🔧 Utils Module (`app/utils/`)

#### `helpers.py`

- **Назначение**: Вспомогательные функции
- **Функции**:
  - `get_or_create_user_settings()` — Получение/создание настроек пользователя
  - `get_env_int()` — Получение переменной окружения как int
  - `get_env_float()` — Получение переменной окружения как float

---

## 🔄 Поток данных

### 1. Сбор метрик

```
APScheduler → collect_metrics_job()
    ↓
SystemMonitor.collect_all_metrics()
    ↓ (psutil)
CPU, RAM, Disk, Net
    ↓
SystemMonitor.save_metrics()
    ↓
PostgreSQL (таблица metrics)
```

### 2. Команда /status

```
User → /status
    ↓
commands.cmd_status()
    ↓
SystemMonitor.get_cpu_metrics()
SystemMonitor.get_memory_metrics()
SystemMonitor.get_disk_metrics()
    ↓
Форматирование текста
    ↓
Отправка пользователю
```

### 3. Команда /graph

```
User → /graph
    ↓
commands.cmd_graph()
    ↓
Отправка inline-клавиатуры
    ↓
User нажимает "6 часов"
    ↓
callbacks.callback_graph()
    ↓
SystemMonitor.get_metrics_for_period(6)
    ↓
ChartGenerator.create_all_charts()
    ↓
4 графика (CPU, RAM, Disk, Net)
    ↓
Отправка как фото
```

### 4. Автоотчёты

```
APScheduler (каждую минуту)
    ↓
send_auto_reports_job()
    ↓
Проверка всех пользователей
    ↓
Если прошло >= report_interval
    ↓
send_report_to_user()
    ↓
Статус + график
    ↓
Обновление last_report_time
```

### 5. Алерты

```
collect_metrics_job()
    ↓
save_metrics()
    ↓
check_alerts(metric)
    ↓
Если CPU/RAM/Disk > порог
    ↓
Отправка алерта всем пользователям
    ↓
Запись времени алерта (cooldown 5 мин)
```

---

## 🐳 Docker структура

### Образы

- `serverstat_app` — Python приложение (бот)
- `postgres:15-alpine` — База данных
- `adminer:latest` — Web-интерфейс для БД

### Volumes

- `postgres_data` — Persistent storage для PostgreSQL
- `./logs:/app/logs` — Bind mount для логов

### Networks

- `serverstat_network` — Bridge network для всех сервисов

### Специальные настройки контейнера app

- `pid: "host"` — Доступ к процессам хоста
- `/proc:/host/proc:ro` — Монтирование /proc
- `/sys:/host/sys:ro` — Монтирование /sys

---

## 🔐 Переменные окружения

### Обязательные

- `TELEGRAM_TOKEN` — Токен бота от BotFather

### База данных

- `DATABASE_URL` — Полный URL подключения
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` — Компоненты

### Настройки мониторинга

- `MONITOR_INTERVAL` — Интервал сбора метрик (секунды, по умолчанию 60)
- `ALERT_CPU_THRESHOLD` — Порог CPU для алертов (%, по умолчанию 90)
- `ALERT_RAM_THRESHOLD` — Порог RAM для алертов (%, по умолчанию 90)
- `ALERT_DISK_THRESHOLD` — Порог Disk для алертов (%, по умолчанию 90)

### Логирование

- `LOG_LEVEL` — Уровень логирования (DEBUG, INFO, WARNING, ERROR)

---

## 📊 Зависимости

### Основные библиотеки

- **aiogram 3.3.0** — Telegram Bot API framework
- **psutil 5.9.6** — Сбор системных метрик
- **matplotlib 3.8.2** — Построение графиков
- **SQLAlchemy 2.0.23** — ORM для БД
- **asyncpg 0.29.0** — PostgreSQL driver
- **APScheduler 3.10.4** — Планировщик задач

### Вспомогательные

- **python-dotenv 1.0.0** — Загрузка .env
- **aiohttp 3.9.1** — HTTP клиент (для aiogram)
- **pillow 10.1.0** — Работа с изображениями

---

## 🎯 Точки расширения

### Добавление новой метрики

1. Обновите модель `Metric` в `app/models/metrics.py`
2. Добавьте метод сбора в `SystemMonitor` (`app/core/monitor.py`)
3. Обновите `collect_all_metrics()` для включения новой метрики
4. Добавьте график в `ChartGenerator` (`app/core/charts.py`) при необходимости

### Добавление новой команды

1. Добавьте handler в `app/bot/handlers/commands.py`
2. Используйте декоратор `@router.message(Command("your_command"))`
3. Обновите `/help` с описанием новой команды

### Добавление новой фоновой задачи

1. Создайте async функцию в `app/core/scheduler.py`
2. Зарегистрируйте её в `init_scheduler()` с нужным триггером
3. Логируйте выполнение для отладки

---

## 📝 Логирование

### Файлы логов

- `bot.log` — Основной лог приложения
- Docker logs — `docker-compose logs -f app`

### Уровни логирования

- **DEBUG** — Детальная информация (метрики, каждое действие)
- **INFO** — Основные события (запуск, отправка отчётов)
- **WARNING** — Предупреждения (не критичные ошибки)
- **ERROR** — Ошибки (исключения, сбои)

---

## 🧪 Тестирование

### Ручное тестирование команд

1. `/start` — Проверка регистрации
2. `/status` — Проверка получения метрик
3. `/graph` → 1 час — Проверка графиков
4. `/history` → 24 часа — Проверка статистики
5. `/top` — Проверка списка процессов
6. `/setinterval 1` → Подождать 1 минуту → Проверка автоотчёта
7. `/stop` — Остановка автоотчётов
8. `/settings` — Проверка отображения настроек

### Проверка алертов

1. Симулируйте высокую нагрузку (stress, yes > /dev/null)
2. Дождитесь превышения порога
3. Проверьте получение алерта в боте

---

## 🔧 Troubleshooting

Смотрите раздел **Troubleshooting** в [README.md](README.md) и [INSTALL.md](INSTALL.md)

---

**Обновлено**: 2025-10-05
