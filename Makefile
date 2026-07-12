COMPOSE = docker compose -f docker/docker-compose.yml --env-file .env

.PHONY: up down down-full restart restart-full exec test lint lint-fix

.env:
	cp .env.example .env

up: .env
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

down-full:
	$(COMPOSE) down -v

restart: down up

restart-full: down-full up

test:
	$(COMPOSE) --profile test up -d --wait test-db
	$(COMPOSE) exec app uv run pytest tests; status=$$?; \
	$(COMPOSE) --profile test rm -fsv test-db; \
	exit $$status

lint:
	$(COMPOSE) exec app uv run ruff check .

lint-fix:
	$(COMPOSE) exec app uv run ruff check --fix .

exec:
	$(COMPOSE) exec app $(filter-out $@,$(MAKECMDGOALS))

.DEFAULT:
	@: