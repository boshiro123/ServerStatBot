# ⚡ Быстрый старт — Server Monitor Bot

## 3 минуты до запуска! 🚀

### 1️⃣ Получите токен (30 секунд)

Откройте Telegram → найдите [@BotFather](https://t.me/BotFather) → отправьте:

```
/newbot
```

Следуйте инструкциям и **скопируйте токен**.

---

### 2️⃣ Клонируйте и настройте (1 минута)

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd ServerStat

# Создайте .env и вставьте токен
cp env.example .env
nano .env  # или vim, или любой редактор
```

В файле `.env` замените `your_bot_token_here` на ваш токен:

```env
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Сохраните (`Ctrl+X`, затем `Y` и `Enter` в nano).

---

### 3️⃣ Запустите (1 минута)

```bash
# Запуск одной командой!
./start.sh
```

Или вручную:

```bash
docker-compose up -d
```

---

### 4️⃣ Проверьте ✅

1. **Откройте вашего бота** в Telegram
2. Отправьте `/start`
3. Попробуйте `/status` — должны появиться метрики!

---

## 🎉 Готово!

Ваш бот работает! Теперь попробуйте:

- `/graph` — Графики метрик
- `/top` — Топ процессов
- `/help` — Все команды

---

## 📊 Бонус: Adminer (управление БД)

Откройте http://localhost:8080

- **Сервер**: `db`
- **Пользователь**: `postgres`
- **Пароль**: `postgres`
- **База данных**: `metrics`

---

## 🔍 Если что-то не работает

### Проверьте логи:

```bash
docker-compose logs -f app
```

### Проверьте контейнеры:

```bash
docker-compose ps
```

Должны быть запущены (Up):

- `serverstat_app`
- `serverstat_db`
- `serverstat_adminer`

### Перезапустите:

```bash
docker-compose restart app
```

---

## 📚 Дальше

- **Полная документация**: [README.md](README.md)
- **Установка без Docker**: [INSTALL.md](INSTALL.md)
- **Структура проекта**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

**С мониторингом! 🖥📊**
