#!/bin/sh
set -e

exec uv run sanic server.app --host 0.0.0.0 --port 8000