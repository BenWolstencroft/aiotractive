lint: ruff mypy

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

.PHONY: ruff mypy lint format dist
