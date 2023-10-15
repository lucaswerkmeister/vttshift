.PHONY: all check

all: requirements.txt dev-requirements.txt check

check:
	black .
	ruff .
	mypy
	pytest

requirements.txt: pyproject.toml
	pip-compile --output-file=$@ $^

dev-requirements.txt: pyproject.toml
	pip-compile --extra=dev --output-file=$@ $^
