# DimaTechLtd

Тестовое REST API на Sanic: пользователи, администраторы, счета, платежи и вебхук пополнения от сторонней платёжной системы.

## Стек

- Python 3.14, [uv](https://docs.astral.sh/uv/)
- Sanic + sanic-ext (Swagger/OpenAPI)
- SQLAlchemy (async) + PostgreSQL
- Alembic (миграции)
- Pydantic (валидация запросов/ответов)
- JWT (авторизация), bcrypt (пароли)

## Запуск через Docker Compose

```bash
make up
```

Поднимутся:
* `db` (Postgres)
* `app`
* `nginx`

При старте `app` автоматически применяет миграции (`alembic upgrade head`) и сидирует тестовые данные (не только данными которые указаны в инструкции, но и дополнительными).

API доступно на `http://localhost/` (port: 80)
Swagger на `http://localhost/docs/swagger`

Полезные команды:

```bash
make down          # остановить контейнеры
make down-full      # остановить и снести volume с данными БД
make restart        # down + up
make restart-full   # down-full + up (чистый старт)
make test           # прогнать тесты внутри контейнера app
make lint           # проверить код ruff'ом внутри контейнера app
make lint-fix       # то же самое, но с автофиксом
make exec <cmd>     # выполнить произвольную команду внутри контейнера app
                     # например: make exec uv run alembic upgrade head
```

## Запуск без Docker

Понадобится локальный/доступный PostgreSQL.

```bash
cp .env.example .env
# в .env поправить DATABASE_URL на реальный адрес Postgres (по умолчанию там хост "db" имя сервиса в docker-сети)

uv sync
uv run alembic upgrade head
uv run python -m app.db.seeds
uv run sanic server.app --host 0.0.0.0 --port 8000
```

API: `http://localhost:8000/`
Swagger: `http://localhost:8000/docs/swagger`.

## Тестовые пользователи (создаются сидом)

| Роль  | Email               | Пароль              |
|-------|---------------------|----------------------|
| Admin | admin@example.com    | 12345!admin54321     |
| User  | user@example.com     | 12345!user54321       |

Помимо основного тестового пользователя сид создаёт ещё 9 обычных пользователей (`user02@example.com` -> `user10@example.com`, тот же пароль) с собственными счетами и платежами, для более реалистичных данных при ручном тестировании списков.

## Авторизация

```
POST /auth/login
{ "email": "...", "password": "..." }
```

Возвращает JWT. Дальше передавать в заголовке `Authorization: Bearer <token>`. В Swagger для этого есть кнопка **Authorize** - достаточно вставить сам токен, без слова `Bearer`.

## Тесты и линтер

```bash
make test       # тесты внутри контейнера app
make lint       # ruff внутри контейнера app
make lint-fix   # ruff --fix внутри контейнера app
```

Тесты не трогают боевую БД `make test` сам поднимает отдельный одноразовый сервис `test-db` (Postgres, без volume, профиль `test` в `docker-compose.yml`) и гоняет всё на нём, включая тесты на конкурентную обработку вебхука (`tests/test_webhook_concurrency.py`), для которых важна настоящая блокировка строк (`SELECT ... FOR UPDATE`) — на SQLite это нельзя проверить достоверно.