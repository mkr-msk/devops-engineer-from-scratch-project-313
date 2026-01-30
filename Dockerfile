FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY main.py ./

# ENV PORT=8080

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "main:app"]