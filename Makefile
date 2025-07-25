.PHONY: db
db:
	@sqlite3 $(shell python -c "from thunter import settings; print(settings.DATABASE)")
