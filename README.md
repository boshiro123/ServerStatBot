# 🖥 Server Monitor Bot

Telegram-бот для мониторинга показателей нагрузки Linux-сервера с автоматической отправкой отчётов и графиков.

## ✨ Возможности

- 📊 **Мониторинг метрик**: CPU, RAM, Disk, Network, Uptime
- 📈 **Графики**: Визуализация метрик за разные периоды (1ч, 6ч, 24ч, 7д)
- 📜 **История**: Текстовые отчёты с статистикой за период
- ⚙️ **Топ процессов**: Список процессов по CPU и RAM
- ⏰ **Автоотчёты**: Настраиваемая автоматическая отправка статуса
- 🚨 **Алерты**: Уведомления при превышении порогов нагрузки
- 🐳 **Docker**: Готовый к деплою через docker-compose

## 🏗 Архитектура

```
ServerStat/
├── app/
│   ├── bot/              # Telegram бот
│   │   ├── handlers/     # Обработчики команд и callback
│   │   ├── keyboards/    # Inline клавиатуры
│   │   └── main.py       # Главный файл бота
│   ├── core/             # Основная логика
│   │   ├── monitor.py    # Сбор метрик (psutil)
│   │   ├── db.py         # Работа с БД
│   │   ├── scheduler.py  # Фоновые задачи
│   │   └── charts.py     # Генерация графиков
│   ├── models/           # Модели БД (SQLAlchemy)
│   └── utils/            # Вспомогательные функции
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## 🚀 Быстрый старт

### 1. Создание Telegram-бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Сохраните полученный токен

### 2. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd ServerStat

# Создайте .env файл из примера
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

### 3. Настройка .env

Создайте файл `.env` со следующим содержимым:

```env
# Telegram Bot Configuration
TELEGRAM_TOKEN=your_bot_token_here

# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=metrics
DB_USER=postgres
DB_PASSWORD=postgres
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/metrics

# Monitoring Settings
MONITOR_INTERVAL=60           # Интервал сбора метрик (секунды)
ALERT_CPU_THRESHOLD=90        # Порог CPU для алертов (%)
ALERT_RAM_THRESHOLD=90        # Порог RAM для алертов (%)
ALERT_DISK_THRESHOLD=90       # Порог Disk для алертов (%)

# Logging
LOG_LEVEL=INFO
```

### 4. Запуск через Docker Compose

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Остановка
docker-compose down
```

### 5. Альтернативный запуск (без Docker)

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Запустите PostgreSQL локально или используйте SQLite
# Для SQLite измените DATABASE_URL в .env:
# DATABASE_URL=sqlite+aiosqlite:///./metrics.db

# Запустите бота
python -m app.bot.main
```

## 📱 Использование бота

### Основные команды

- `/start` — Начало работы с ботом
- `/help` — Справка по командам
- `/status` — Текущие показатели сервера
- `/graph` — Графики метрик (выбор периода)
- `/history` — Статистика за период
- `/top` — Топ процессов по CPU и RAM
- `/setinterval <минуты>` — Включить автоотправку отчётов
- `/stop` — Остановить автоотправку
- `/settings` — Ваши текущие настройки

### Примеры использования

**Просмотр текущего статуса:**

```
/status
```

Ответ:

```
📊 Текущее состояние сервера

🖥 CPU:
  • Использование: 23.4%
  • Load Avg: 0.12 / 0.18 / 0.25

🧠 RAM:
  • 3.20 GB / 8.00 GB (40.0%)

💾 Disk:
  • 42.00 GB / 100.00 GB (42.0%)

🌐 Network:
  • ↑ Отправлено: 320.50 MB
  • ↓ Получено: 820.30 MB

⏱ Uptime: 1д 3ч 22м
⚙️ Процессов: 142
```

**Получение графиков:**

```
/graph
```

→ Выберите период (1ч, 6ч, 24ч, 7д) → Получите 4 графика (CPU, RAM, Disk, Network)

**Настройка автоотправки:**

```
/setinterval 60
```

→ Бот будет отправлять статус каждые 60 минут

**Остановка автоотправки:**

```
/stop
```

## 🔧 Конфигурация

### Настройка порогов алертов

В файле `.env` можно настроить пороги для уведомлений:

```env
ALERT_CPU_THRESHOLD=90     # CPU > 90% → алерт
ALERT_RAM_THRESHOLD=90     # RAM > 90% → алерт
ALERT_DISK_THRESHOLD=90    # Disk > 90% → алерт
```

### Изменение интервала сбора метрик

```env
MONITOR_INTERVAL=60  # Сбор метрик каждые 60 секунд
```

Меньшее значение = более детальные графики, но больше записей в БД.

## 📊 База данных

Приложение использует PostgreSQL (или SQLite) для хранения метрик.

### Просмотр базы данных

**Через Adminer (включён в docker-compose):**

1. Откройте http://localhost:8080
2. Параметры подключения:
   - Сервер: `db`
   - Пользователь: `postgres`
   - Пароль: `postgres`
   - База данных: `metrics`

### Структура таблиц

**metrics** — метрики системы:

```sql
- id (PK)
- timestamp
- cpu_load_1m, cpu_load_5m, cpu_load_15m
- cpu_percent, cpu_temp
- ram_used, ram_total, ram_percent
- disk_used, disk_total, disk_percent
- net_sent, net_recv
- process_count
```

**user_settings** — настройки пользователей:

```sql
- user_id (PK)
- username
- auto_report_enabled
- report_interval
- last_report_time
- alerts_enabled
- created_at, updated_at
```

## 🐳 Docker

### Управление контейнерами

```bash
# Запуск
docker-compose up -d

# Просмотр статуса
docker-compose ps

# Логи бота
docker-compose logs -f app

# Логи базы данных
docker-compose logs -f db

# Перезапуск
docker-compose restart app

# Остановка
docker-compose down

# Остановка с удалением данных
docker-compose down -v
```

### Обновление приложения

```bash
# Пересборка образа
docker-compose build app

# Перезапуск с новым образом
docker-compose up -d --build app
```

## 📝 Логирование

Логи сохраняются в:

- Внутри контейнера: `/app/bot.log`
- На хосте: `./logs/bot.log`

Просмотр логов:

```bash
# Логи Docker
docker-compose logs -f app

# Логи файла
tail -f logs/bot.log
```

## ⚠️ Важные замечания

### Доступ к метрикам хоста

Для корректного сбора метрик в Docker:

1. Контейнер работает с `pid: "host"` для доступа к процессам
2. Монтируются `/proc` и `/sys` из хоста
3. Это необходимо для получения реальных метрик сервера

### Безопасность

- **Не коммитьте .env файл** с токеном бота
- Используйте сильные пароли для PostgreSQL
- Ограничьте доступ к порту Adminer (8080)
- Рассмотрите использование reverse proxy с SSL

### Производительность

- При `MONITOR_INTERVAL=60` и хранении данных за 7 дней будет ~10k записей
- Рекомендуется настроить очистку старых данных (можно добавить cron задачу)

## 🔍 Troubleshooting

### Бот не отвечает

```bash
# Проверьте статус контейнера
docker-compose ps

# Проверьте логи
docker-compose logs app

# Проверьте токен бота в .env
cat .env | grep TELEGRAM_TOKEN
```

### Ошибка подключения к БД

```bash
# Проверьте статус PostgreSQL
docker-compose ps db

# Проверьте логи БД
docker-compose logs db

# Перезапустите БД
docker-compose restart db
```

### Не собираются метрики

```bash
# Убедитесь, что контейнер имеет доступ к хосту
docker-compose exec app python -c "import psutil; print(psutil.cpu_percent())"
```

### График не генерируется

- Проверьте, что данные есть в БД (через Adminer)
- Убедитесь, что прошло достаточно времени для накопления метрик
- Проверьте логи на ошибки matplotlib

## 🛠 Разработка

### Локальная разработка

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Запустите в режиме разработки
python -m app.bot.main
```

### Добавление новых функций

1. **Новая команда**: добавьте handler в `app/bot/handlers/commands.py`
2. **Новая метрика**: обновите `app/core/monitor.py` и модель в `app/models/metrics.py`
3. **Новый график**: добавьте метод в `app/core/charts.py`

## 📄 Лицензия

MIT License

## 🤝 Вклад

Pull requests приветствуются! Для больших изменений сначала откройте issue для обсуждения.

## 📞 Поддержка

При возникновении проблем:

1. Проверьте раздел Troubleshooting
2. Изучите логи: `docker-compose logs -f`
3. Создайте issue с описанием проблемы

---

**Создано с ❤️ для мониторинга серверов**
