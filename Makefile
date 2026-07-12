.env:
	cp .env.example .env

up: .env
	docker compose -f docker/docker-compose.yml up --build

down:
	docker compose -f docker/docker-compose.yml down

down-v:
	docker compose -f docker/docker-compose.yml down -v