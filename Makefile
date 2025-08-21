.DEFAULT_GOAL := help
VENV = .venv
DIST = dist

.PHONY: help
help:
	@echo "'make test lint' for testing and linting."
	@echo "You can use 'uv' or 'pip' to install thunter CLI tool from source to play around with your latest version"

.PHONY: lint
lint: $(VENV)/bin/activate
	$(VENV)/bin/ruff check

.PHONY: format
format: $(VENV)/bin/activate
	$(VENV) ruff check --fix

.PHONY: test
test: $(VENV)/bin/activate
	$(VENV)/bin/coverage run -m unittest
	$(VENV)/bin/coverage report

.PHONY: clean
clean:
	rm -rf thunter/__pycache__
	rm -rf .venv

.PHONY: build
build:
	uv build

.PHONY: upload
upload:
	uv run twine check $(DIST)/* && uv run twine upload $(DIST)/*

$(VENV)/bin/activate: pyproject.toml
	uv sync