.PHONY: db
db:
	@sqlite3 $(shell python -c "from hunt import settings; print(settings.DATABASE)")
