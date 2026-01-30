#!/bin/bash
set -e

uv run alembic upgrade head
exec uv run gunicorn --bind 0.0.0.0:${PORT} --workers 2 main:app