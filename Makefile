run:
	uv run python main.py
	
test:
	uv run pytest -v

lint:
	uv run ruff check .

check: lint test

.PHONY: run test lint check