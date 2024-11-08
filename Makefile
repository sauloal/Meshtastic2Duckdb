API_HOST=127.0.0.1
API_PORT=8000
API_DB_FILE=meshtastic_logger.duckdb

all: help

help:
	@echo server
	@echo server-dev
	@echo openapi
	@echo curl
	@echo
	@echo logger
	@echo
	@echo venv
	@echo install
	@echo
	@echo dump

.PHONY: server server-dev openapi curl
.PHONY: logger
.PHONY: venv install
.PHONY: dump

server:
	. .venv/bin/activate && fastapi run app/main.py

server-dev:
	. .venv/bin/activate && fastapi dev app/main.py

openapi:
	curl -v $(API_HOST):$(API_PORT)/openapi.json | jq -C | less -SR

curl:
	curl -v "$(API_HOST):$(API_PORT)"
	curl -v "$(API_HOST):$(API_PORT)/api"
	curl -v "$(API_HOST):$(API_PORT)/api/dbs"
	curl -v "$(API_HOST):$(API_PORT)/api/dbs/$(API_DB_FILE)"
	curl -v "$(API_HOST):$(API_PORT)/api/dbs/$(API_DB_FILE)/models"
	curl -v "$(API_HOST):$(API_PORT)/api/dbs/$(API_DB_FILE)/models/nodes"
	curl -v "$(API_HOST):$(API_PORT)/api/dbs/$(API_DB_FILE)/models/nodes?dry-run=true" \
		-H 'content-type: application/json' \
		-X POST \
		-d '{"hopsAway": 0, "lastHeard": 1731060061, "num": 4175865308, "snr": 16.5, "isFavorite": null, "airUtilTx": 3.0786943, "batteryLevel": 75, "channelUtilization": 5.9116664, "uptimeSeconds": 176372, "voltage": 3.942, "altitude": null, "latitude": null, "latitudeI": null, "longitude": null, "longitudeI": null, "time": null, "hwModel": "TRACKER_T1000_E", "user_id": "f8e6a5dc", "longName": "Saulo", "macaddr": "/pf45qXc", "publicKey": "zd9XSkmI+ptPM6H+PlReOTL2d5iCW6S/YHe3cGbQen4=", "role": "TRACKER", "shortName": "SAAA", "id": null}'

logger:
	. .venv/bin/activate && python3 logger.py



venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip3 install -r requirements.txt



dump:
	. .venv/bin/activate && echo .dump | duckdb $(API_DB_FILE)
