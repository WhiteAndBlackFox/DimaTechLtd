#!/bin/sh
set -e

uv run alembic upgrade head
uv run python -m app.db.seeds

exec uv run sanic server.app --host 0.0.0.0 --port 8000 -r