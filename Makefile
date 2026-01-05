lint: ruff mypy

test:
	pytest tests/ -v --cov=aiotractive --cov-report=term-missing

format:
	ruff format .

ruff:
	ruff check .
	ruff format .

mypy:
	mypy aiotractive

dist:
	python setup.py sdist bdist_wheel
	twine check dist/*

.PHONY: ruff mypy lint format test dist
