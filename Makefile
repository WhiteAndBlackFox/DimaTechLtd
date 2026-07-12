COMPOSE = docker compose -f docker/docker-compose.yml --env-file .env

.PHONY: up down down-full restart restart-full exec

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

exec:
	$(COMPOSE) exec app $(filter-out $@,$(MAKECMDGOALS))

.DEFAULT:
	@: