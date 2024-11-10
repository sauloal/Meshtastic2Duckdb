.SHELL:=/bin/bash

ifeq ($${MESH_LOGGER_REMOTE_HTTP_HOST},)
$(warning MESH_LOGGER_REMOTE_HTTP_HOST not defined)
endif

ifeq ($${MESH_LOGGER_REMOTE_HTTP_PORT},)
$(warning MESH_LOGGER_REMOTE_HTTP_PORT not defined)
endif

ifeq ($${MESH_LOGGER_DB_FILENAME},)
$(warning MESH_LOGGER_DB_FILENAME not defined)
endif

all: help

help:
	@echo "HELP"
	@echo "  server"
	@echo "  server-dev"
	@echo "  openapi"
	@echo "  curl"
	@echo
	@echo "  logger"
	@echo
	@echo "  venv"
	@echo "  install"
	@echo
	@echo "  dump"
	@echo "  schema"
	@echo

.PHONY: server server-dev openapi curl
.PHONY: logger
.PHONY: venv install
.PHONY: dump schema

server:
	export `cat config.env` && . .venv/bin/activate && fastapi run app/main.py --host="$${MESH_LOGGER_REMOTE_HTTP_HOST}" --port="$${MESH_LOGGER_REMOTE_HTTP_PORT}"

server-dev:
	export `cat config.env` && . .venv/bin/activate && fastapi dev app/main.py --host="$${MESH_LOGGER_REMOTE_HTTP_HOST}" --port="$${MESH_LOGGER_REMOTE_HTTP_PORT}"

openapi:
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/openapi.json" | jq -C | less -SR

curl:
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}"
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api"
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs"
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}"
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}/models"
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}/models/nodes"
	export `cat config.env` && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}/models/nodes?dry-run=true" \
		-H 'content-type: application/json' \
		-X POST \
		-d '{"hopsAway": 0, "lastHeard": 1731060061, "num": 4175865308, "snr": 16.5, "isFavorite": null, "airUtilTx": 3.0786943, "batteryLevel": 75, "channelUtilization": 5.9116664, "uptimeSeconds": 176372, "voltage": 3.942, "altitude": null, "latitude": null, "latitudeI": null, "longitude": null, "longitudeI": null, "time": null, "hwModel": "TRACKER_T1000_E", "user_id": "f8e6a5dc", "longName": "Saulo", "macaddr": "/pf45qXc", "publicKey": "zd9XSkmI+ptPM6H+PlReOTL2d5iCW6S/YHe3cGbQen4=", "role": "TRACKER", "shortName": "SAAA", "id": null}'

logger:
	export `cat config.env` && . .venv/bin/activate && python3 logger.py



venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip3 install -r requirements.txt



dump:
	export TS=`date +%s` ; \
	export `cat config.env` && . .venv/bin/activate && echo .dump   | duckdb $${MESH_LOGGER_DB_FILENAME} > /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	cat /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	rm  /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS}

schema:
	export TS=`date +%s` ; \
	export `cat config.env` && . .venv/bin/activate && echo .schema | duckdb $${MESH_LOGGER_DB_FILENAME} > /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	cat /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	rm  /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS}

