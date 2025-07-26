.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Try 'make install' or 'make develop' to start using Hunt"
	@echo "'make db' will open the Hunt database in SQLite for direct access if needed, but hunt 'edit' should be preferred"

.PHONY: install
install:
	pip install .

.PHONY: uninstall
install:
	pip uninstall .

.PHONY: develop
develop:
	pip install -e .

.PHONY: clean
clean:
	rm -fr ~/.thunter
	rm -fr hunt.egg-info/
	rm -fr thunter/__pycache__/

.PHONY: lint
lint:
	find . -type f -name '*.py' | xargs flake8

.PHONY: db
db:
	@sqlite3 $(shell python -c "from thunter import settings; print(settings.DATABASE)")
