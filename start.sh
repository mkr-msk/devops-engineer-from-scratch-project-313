#!/bin/bash
set -e

envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

uv run alembic upgrade head

nginx

exec uv run gunicorn --bind 127.0.0.1:8080 --workers 2 app.main:app