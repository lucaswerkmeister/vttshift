.PHONY: all check

all: requirements.txt dev-requirements.txt check

check:
	pytest

requirements.txt: pyproject.toml
	pip-compile --output-file=$@ $^

dev-requirements.txt: pyproject.toml
	pip-compile --extra=dev --output-file=$@ $^
