.PHONY: help build up down restart logs clean

help:
	@echo "Server Monitor Bot - Makefile команды:"
	@echo ""
	@echo "  make build      - Собрать Docker образ"
	@echo "  make up         - Запустить все сервисы"
	@echo "  make down       - Остановить все сервисы"
	@echo "  make restart    - Перезапустить бота"
	@echo "  make logs       - Показать логи бота"
	@echo "  make logs-db    - Показать логи базы данных"
	@echo "  make clean      - Остановить и удалить все контейнеры и volumes"
	@echo "  make shell      - Открыть shell в контейнере бота"
	@echo "  make db-shell   - Открыть psql в контейнере БД"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Сервисы запущены!"
	@echo "📊 Adminer доступен на http://localhost:8080"

down:
	docker-compose down

restart:
	docker-compose restart app

logs:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f db

clean:
	docker-compose down -v
	@echo "🧹 Все контейнеры и данные удалены"

shell:
	docker-compose exec app /bin/bash

db-shell:
	docker-compose exec db psql -U postgres -d metrics

status:
	docker-compose ps

