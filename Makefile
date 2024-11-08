all: help

help:
	@echo server
	@echo server-dev
	@echo openapi
	@echo
	@echo logger
	@echo
	@echo venv
	@echo install
	@echo
	@echo dump

.PHONY: server server-dev openapi
.PHONY: logger
.PHONY: venv install
.PHONY: dump

server:
	. .venv/bin/activate && fastapi run app.py

server-dev:
	. .venv/bin/activate && fastapi dev app.py

openapi:
	curl -v 127.0.0.1:8000/openapi.json | jq -C | less -SR

logger:
	. .venv/bin/activate && python3 logger.py



venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip3 install -r requirements.txt



dump:
	. .venv/bin/activate && echo .dump | duckdb meshtastic_logger.duckdb
