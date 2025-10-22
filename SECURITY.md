# 🔒 Безопасность Server Monitor Bot

## Реализованные меры безопасности

### 1. Непривилегированный пользователь

**Dockerfile:**

- Контейнер app запускается от пользователя `appuser` (UID 1000), а не от root
- Минимизирует риск при компрометации контейнера
- Ограничивает возможность изменения системных файлов

### 2. Ограничение capabilities (Linux capabilities)

**Контейнер `app`:**

```yaml
cap_drop:
  - ALL # Убираем все capabilities
cap_add:
  - SYS_PTRACE # Только для мониторинга процессов
```

**Контейнер `db`:**

```yaml
cap_drop:
  - ALL
cap_add:
  - CHOWN # Для управления правами файлов
  - DAC_OVERRIDE # Для доступа к данным
  - SETGID # Для смены группы
  - SETUID # Для смены пользователя
```

**Контейнер `adminer`:**

```yaml
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETGID
  - SETUID
  - NET_BIND_SERVICE # Для биндинга порта
```

### 3. Security Options

**Все контейнеры:**

```yaml
security_opt:
  - no-new-privileges:true # Запрет повышения привилегий
```

Это предотвращает использование SUID/SGID бинарников для эскалации привилегий.

### 4. Ограничение сетевого доступа

**PostgreSQL и Adminer:**

```yaml
ports:
  - "127.0.0.1:5433:5432" # Только localhost
  - "127.0.0.1:8080:8080" # Только localhost
```

- Доступ к БД и Adminer **только с локального хоста**
- Извне порты недоступны
- Для удалённого доступа используйте SSH туннель

### 5. Read-only монтирование

**Критические директории:**

```yaml
volumes:
  - /proc:/host/proc:ro # read-only
  - /sys:/host/sys:ro # read-only
```

- Только чтение системных метрик
- Невозможность модификации хостовой системы

**Adminer:**

```yaml
read_only: true # Весь filesystem read-only
tmpfs:
  - /tmp:noexec,nosuid,size=50m # Временные файлы в tmpfs
```

### 6. Защищённый tmpfs

**Все контейнеры:**

```yaml
tmpfs:
  - /tmp:noexec,nosuid,size=100m
```

- `noexec` — запрет выполнения файлов из /tmp
- `nosuid` — игнорирование SUID бита
- Ограничение размера

### 7. Ограничение ресурсов (DoS protection)

**Контейнер `app`:**

```yaml
resources:
  limits:
    cpus: "1.0" # Максимум 1 CPU
    memory: 512M # Максимум 512 МБ RAM
  reservations:
    cpus: "0.25" # Минимум 0.25 CPU
    memory: 128M # Минимум 128 МБ RAM
```

**Контейнер `db`:**

```yaml
resources:
  limits:
    cpus: "1.0"
    memory: 512M
```

**Контейнер `adminer`:**

```yaml
resources:
  limits:
    cpus: "0.5"
    memory: 256M
```

### 8. Healthchecks

**PostgreSQL:**

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**App (в Dockerfile):**

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
```

### 9. Изолированная сеть

```yaml
networks:
  default:
    name: serverstat_network
```

- Контейнеры изолированы в своей сети
- Нет доступа к другим Docker сетям

### 10. Минимальный базовый образ

```dockerfile
FROM python:3.11-slim
```

- Используется slim версия (меньше уязвимостей)
- Удаление пакетов после установки зависимостей

---

## Векторы атак и защита

### ⚠️ Вектор 1: Компрометация через уязвимость в зависимостях

**Защита:**

- ✅ Регулярно обновляйте зависимости: `pip install --upgrade`
- ✅ Используйте сканеры уязвимостей: `pip-audit` или `safety`
- ✅ Фиксируйте версии в `requirements.txt`

**Проверка:**

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### ⚠️ Вектор 2: Инъекция через Telegram команды

**Защита:**

- ✅ Используется HTML parse mode (не Markdown)
- ✅ Все входные данные валидируются
- ✅ Параметры команд парсятся безопасно

### ⚠️ Вектор 3: SQL Injection

**Защита:**

- ✅ Используется SQLAlchemy ORM (параметризованные запросы)
- ✅ Нет raw SQL запросов
- ✅ Типизированные параметры

### ⚠️ Вектор 4: Эскалация привилегий в контейнере

**Защита:**

- ✅ `no-new-privileges:true` — запрет повышения привилегий
- ✅ Запуск от непривилегированного пользователя
- ✅ Минимальные capabilities

### ⚠️ Вектор 5: Выход из контейнера (container breakout)

**Защита:**

- ✅ `pid: "host"` нужен для мониторинга, но риск минимизирован:
  - Read-only монтирование /proc и /sys
  - Запрет повышения привилегий
  - Минимальные capabilities (только SYS_PTRACE)
- ✅ Не используется `privileged: true`

### ⚠️ Вектор 6: DoS через потребление ресурсов

**Защита:**

- ✅ Жёсткие лимиты CPU и RAM
- ✅ Ограничение tmpfs
- ✅ Restart политика: `unless-stopped`

### ⚠️ Вектор 7: Утечка токена бота

**Защита:**

- ✅ Токен в переменных окружения (не в коде)
- ✅ `.env` в `.gitignore`
- ✅ Рекомендация: используйте Docker secrets в production

### ⚠️ Вектор 8: Атака на PostgreSQL извне

**Защита:**

- ✅ Порт привязан только к localhost
- ✅ Изолированная Docker сеть
- ✅ Требуется SSH туннель для удалённого доступа

### ⚠️ Вектор 9: Атака на Adminer

**Защита:**

- ✅ Доступ только с localhost
- ✅ Read-only filesystem
- ✅ Рекомендация: отключайте в production или защитите nginx с basic auth

---

## Рекомендации для production

### 1. Отключите Adminer

В production среде отключите Adminer или защитите его:

```yaml
# Закомментируйте в docker-compose.yml
# adminer:
#   ...
```

Или добавьте nginx с basic auth перед ним.

### 2. Используйте Docker Secrets

Вместо `.env` файла:

```yaml
secrets:
  telegram_token:
    external: true

services:
  app:
    secrets:
      - telegram_token
```

### 3. Регулярно обновляйте образы

```bash
docker-compose pull
docker-compose build --no-cache
docker-compose up -d
```

### 4. Мониторинг логов

```bash
# Настройте централизованное логирование
docker-compose logs --tail=100 -f | grep -i error
```

### 5. Backup базы данных

```bash
docker exec serverstat_db pg_dump -U postgres metrics > backup.sql
```

### 6. Ротация логов

Добавьте ротацию для `logs/bot.log`:

```bash
# /etc/logrotate.d/serverstat
/path/to/ServerStat/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### 7. Firewall правила

```bash
# Разрешите только SSH и необходимые порты
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw enable
```

### 8. SSH туннель для удалённого доступа

Для доступа к PostgreSQL/Adminer удалённо:

```bash
ssh -L 5433:localhost:5433 -L 8080:localhost:8080 user@server
```

Теперь открывайте http://localhost:8080 локально.

### 9. Сканирование уязвимостей

```bash
# Trivy - сканер Docker образов
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image serverstat_app

# pip-audit - сканер Python зависимостей
pip install pip-audit
pip-audit
```

### 10. Используйте неroot пользователя на хосте

```bash
# Не запускайте docker-compose от root
sudo usermod -aG docker $USER
newgrp docker
docker-compose up -d
```

---

## Проверка безопасности

### Чеклист

- [ ] Контейнеры запускаются от непривилегированных пользователей
- [ ] Все sensitive данные в `.env`, который в `.gitignore`
- [ ] Порты БД и Adminer доступны только с localhost
- [ ] Capabilities минимальны для каждого контейнера
- [ ] `no-new-privileges:true` включён
- [ ] Ограничения ресурсов настроены
- [ ] Healthchecks работают
- [ ] Логи мониторятся
- [ ] Backup БД настроен
- [ ] Зависимости регулярно обновляются

### Аудит безопасности

```bash
# Docker Bench Security
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /var/lib:/var/lib -v /var/run/docker.sock:/var/run/docker.sock \
  docker/docker-bench-security

# Проверка запущенных контейнеров
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Проверка capabilities
docker inspect serverstat_bot | grep -A 20 CapAdd
```

---

## Что НЕ защищено

### Ограничения текущей конфигурации

1. **`pid: "host"`** — даёт доступ к процессам хоста

   - **Риск**: теоретически возможен container breakout
   - **Митигация**: минимальные capabilities, read-only монтирование
   - **Альтернатива**: мониторить только контейнер (без хостовых метрик)

2. **Токен в переменной окружения**

   - **Риск**: видим через `docker inspect`
   - **Митигация**: используйте Docker Secrets в production

3. **Нет SSL для PostgreSQL**
   - **Риск**: трафик в незашифрованном виде внутри Docker сети
   - **Митигация**: Docker сеть изолирована, но можно добавить SSL

---

## Итоги улучшений безопасности

✅ **10+ мер безопасности реализовано**
✅ **Минимальные привилегии**
✅ **Изоляция контейнеров**
✅ **Ограничение ресурсов**
✅ **Защита от распространённых атак**

**Баланс**: Максимальная безопасность при сохранении функциональности мониторинга.

---

**Обновлено**: 2025-10-05
