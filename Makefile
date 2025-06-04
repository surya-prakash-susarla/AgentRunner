.PHONY: install format lint test clean

install:
	pip install -e ".[dev]"

format:
	black src tests
	isort src tests

lint:
	black --check src tests
	isort --check-only src tests
	mypy src
	ruff check src tests

test:
	pytest

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +

setup: clean install format lint test
