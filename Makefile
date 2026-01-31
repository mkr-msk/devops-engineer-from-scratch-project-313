run:
	uv run python main.py
	
test:
	uv run pytest -v

lint:
	uv run ruff check .

check: lint test

migrate:
	uv run alembic upgrade head

dev:
	npm run dev

.PHONY: run test lint check migrate dev