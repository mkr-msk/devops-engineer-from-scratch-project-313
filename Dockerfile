FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY public /app/public

COPY app ./app
COPY main.py ./

COPY alembic.ini ./
COPY alembic ./alembic

COPY nginx.conf /etc/nginx/nginx.conf.template

COPY start.sh ./
RUN chmod +x /app/start.sh

ENV PORT=80

CMD ["/app/start.sh"] 