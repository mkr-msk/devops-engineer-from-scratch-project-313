FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    nginx \
    gettext-base \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

RUN mkdir -p /app/public && \
    cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

COPY app ./app
COPY main.py ./

COPY alembic.ini ./
COPY alembic ./alembic

COPY nginx.conf /etc/nginx/nginx.conf.template

COPY start.sh ./
RUN chmod +x /app/start.sh

ENV PORT=80

CMD ["/app/start.sh"] 