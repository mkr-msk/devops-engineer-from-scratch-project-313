run:
	uv run python main.py

prod-run:
	uv run gunicorn --bind 0.0.0.0:${PORT} --workers 2 main:app
	
test:
	uv run pytest -v

lint:
	uv run ruff check .

check: lint test

.PHONY: run test lint check