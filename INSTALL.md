# 📥 Инструкция по установке Server Monitor Bot

## Быстрая установка (Linux/macOS)

### Шаг 1: Получите токен бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен (формат: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Шаг 2: Клонируйте репозиторий

```bash
git clone <your-repo-url>
cd ServerStat
```

### Шаг 3: Настройте окружение

```bash
# Создайте .env файл
cp env.example .env

# Отредактируйте .env и вставьте ваш токен
nano .env
# или
vim .env
```

В файле `.env` замените:

```env
TELEGRAM_TOKEN=your_bot_token_here
```

на:

```env
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Шаг 4: Запустите бота

```bash
# Используйте скрипт быстрого запуска
./start.sh

# Или вручную через docker-compose
docker-compose up -d
```

### Шаг 5: Проверьте работу

```bash
# Просмотрите логи
docker-compose logs -f app

# Проверьте статус контейнеров
docker-compose ps
```

Откройте вашего бота в Telegram и отправьте `/start`

---

## Установка на Windows

### Шаг 1: Установите необходимое ПО

1. **Docker Desktop**: https://www.docker.com/products/docker-desktop/

   - Скачайте и установите
   - Перезагрузите компьютер
   - Запустите Docker Desktop

2. **Git** (если нужно): https://git-scm.com/download/win

### Шаг 2: Клонируйте репозиторий

```powershell
git clone <your-repo-url>
cd ServerStat
```

### Шаг 3: Настройте окружение

1. Скопируйте файл `env.example` в `.env`:

   ```powershell
   copy env.example .env
   ```

2. Откройте `.env` в блокноте:

   ```powershell
   notepad .env
   ```

3. Замените `your_bot_token_here` на ваш токен от BotFather

### Шаг 4: Запустите бота

```powershell
# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f app
```

---

## Установка без Docker (локальная установка)

### Требования

- Python 3.11+
- PostgreSQL 13+ (или можно использовать SQLite)

### Шаг 1: Создайте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

### Шаг 2: Установите зависимости

```bash
pip install -r requirements.txt
```

### Шаг 3: Настройте базу данных

**Вариант А: PostgreSQL**

```bash
# Установите PostgreSQL
# Linux (Ubuntu/Debian):
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Создайте базу данных
sudo -u postgres psql
CREATE DATABASE metrics;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE metrics TO postgres;
\q
```

**Вариант Б: SQLite (проще для тестирования)**

В файле `.env` измените:

```env
DATABASE_URL=sqlite+aiosqlite:///./metrics.db
```

### Шаг 4: Настройте .env

```bash
cp env.example .env
nano .env
```

Для локального запуска измените:

```env
TELEGRAM_TOKEN=your_bot_token_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/metrics
# или для SQLite:
# DATABASE_URL=sqlite+aiosqlite:///./metrics.db
```

### Шаг 5: Запустите бота

```bash
python -m app.bot.main
```

---

## Проверка установки

### 1. Проверьте логи

**Docker:**

```bash
docker-compose logs -f app
```

Должно быть:

```
INFO - Инициализация базы данных...
INFO - База данных успешно инициализирована
INFO - Инициализация планировщика...
INFO - Планировщик инициализирован
INFO - Планировщик запущен
INFO - Бот запущен и готов к работе!
```

### 2. Откройте бота в Telegram

- Найдите вашего бота по username
- Отправьте `/start`
- Должно прийти приветственное сообщение

### 3. Проверьте команды

- `/status` — должны появиться текущие метрики
- `/help` — должна появиться справка

### 4. Проверьте сбор метрик

Подождите 1-2 минуты, затем:

- `/graph` → выберите "1 час"
- Должны появиться графики (если данные уже накоплены)

### 5. Проверьте базу данных

**Docker (Adminer):**

- Откройте http://localhost:8080
- Подключитесь: сервер=`db`, пользователь=`postgres`, пароль=`postgres`
- Должны быть таблицы `metrics` и `user_settings`
- В таблице `metrics` должны появляться новые записи

---

## Возможные проблемы

### ❌ Ошибка: "TELEGRAM_TOKEN не установлен"

**Решение:**

- Проверьте наличие файла `.env`
- Убедитесь, что в `.env` есть строка `TELEGRAM_TOKEN=ваш_токен`
- Токен должен быть без кавычек

### ❌ Ошибка: "Cannot connect to the Docker daemon"

**Решение:**

- Убедитесь, что Docker запущен: `docker ps`
- Linux: добавьте пользователя в группу docker: `sudo usermod -aG docker $USER`
- Перезагрузите терминал/систему

### ❌ Ошибка: "Port 5432 already in use"

**Решение:**

- У вас уже запущен PostgreSQL локально
- Вариант 1: Остановите локальный PostgreSQL: `sudo systemctl stop postgresql`
- Вариант 2: Измените порт в `docker-compose.yml`: `"5433:5432"`

### ❌ Бот не отвечает

**Решение:**

1. Проверьте логи: `docker-compose logs app`
2. Проверьте токен: токен должен быть актуальным
3. Проверьте интернет-соединение
4. Перезапустите: `docker-compose restart app`

### ❌ Нет данных для графиков

**Решение:**

- Подождите 5-10 минут для накопления данных
- Проверьте, что метрики собираются: `docker-compose logs app | grep "Метрики собраны"`
- Проверьте БД через Adminer — должны быть записи в таблице `metrics`

---

## Обновление бота

### Docker

```bash
# Получите последние изменения
git pull

# Пересоберите и перезапустите
docker-compose down
docker-compose build
docker-compose up -d
```

### Локальная установка

```bash
# Получите последние изменения
git pull

# Обновите зависимости
pip install -r requirements.txt --upgrade

# Перезапустите бота
# Ctrl+C для остановки
python -m app.bot.main
```

---

## Удаление

### Docker (полное удаление)

```bash
# Остановка и удаление контейнеров
docker-compose down

# Удаление с данными
docker-compose down -v

# Удаление образов
docker rmi serverstat_app
```

### Локальная установка

```bash
# Деактивируйте виртуальное окружение
deactivate

# Удалите папку проекта
rm -rf ServerStat

# Удалите базу данных (PostgreSQL)
sudo -u postgres psql
DROP DATABASE metrics;
\q
```

---

## Дополнительная помощь

- 📖 Полная документация: [README.md](README.md)
- 🐛 Проблемы: [GitHub Issues]
- 💬 Обсуждение: [Telegram/Discord]

**Удачи в мониторинге! 🚀**
