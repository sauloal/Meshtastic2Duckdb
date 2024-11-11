.SHELL:=/bin/bash

all: help

help:
	@echo "HELP"
	@echo "  local-config"
	@echo
	@echo "  logger"
	@echo
	@echo "  server"
	@echo "  server-dev"
	@echo "  openapi"
	@echo "  curl"
	@echo
	@echo "  dump"
	@echo "  schema"
	@echo
	@echo "  venv"
	@echo "  install"
	@echo
	@echo "  docker-build"
	@echo "  docker-config"
	@echo "  docker-restart"
	@echo "  docker-up"
	@echo "  docker-down"
	@echo "  docker-logs"
	@echo "  docker-ps"
	@echo "  docker-run-logger"
	@echo "  docker-run-server"
	@echo






.PHONY: local-config
.PHONY: logger
.PHONY: server server-dev openapi curl

local-config:
	@echo 'export `cat config.env`; export `envsubst < config.env`'

logger:
	. .venv/bin/activate && cd meshtastic2duckdb     && python3 -m logger.logger

server:
	. .venv/bin/activate && cd meshtastic2duckdb/app && fastapi run main.py --host="$${MESH_APP_HOST}" --port="$${MESH_APP_PORT}"

server-dev:
	. .venv/bin/activate && cd meshtastic2duckdb/app && fastapi dev main.py --host="$${MESH_APP_HOST}" --port="$${MESH_APP_PORT}"

openapi:
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/openapi.json" | jq -C | less -SR

curl:
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}"
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api"
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs"
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}"
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}/models"
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}/models/nodes"
	curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/dbs/$${MESH_LOGGER_DB_FILENAME}/models/nodes?dry-run=true" \
		-H 'content-type: application/json' \
		-X POST \
		-d '{"hopsAway": 0, "lastHeard": 1731060061, "num": 4175865308, "snr": 16.5, "isFavorite": null, "airUtilTx": 3.0786943, "batteryLevel": 75, "channelUtilization": 5.9116664, "uptimeSeconds": 176372, "voltage": 3.942, "altitude": null, "latitude": null, "latitudeI": null, "longitude": null, "longitudeI": null, "time": null, "hwModel": "TRACKER_T1000_E", "user_id": "f8e6a5dc", "longName": "Saulo", "macaddr": "/pf45qXc", "publicKey": "zd9XSkmI+ptPM6H+PlReOTL2d5iCW6S/YHe3cGbQen4=", "role": "TRACKER", "shortName": "SAAA", "id": null}'





.PHONY: dump schema

dump:
	export TS=`date +%s` ; \
	. .venv/bin/activate && echo .dump   | duckdb meshtastic2duckdb/app/dbs/$${MESH_LOGGER_DB_FILENAME} > /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	cat /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	rm  /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS}

schema:
	export TS=`date +%s` ; \
	. .venv/bin/activate && echo .schema | duckdb meshtastic2duckdb/app/dbs/$${MESH_LOGGER_DB_FILENAME} > /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	cat /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	rm  /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS}





.PHONY: venv install

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip3 install -r requirements.txt





.PHONY: docker-build docker-config docker-restart docker-up docker-down docker-logs docker-ps docker-run-logger docker-run-server

docker-build:
	docker compose build

docker-config:
	docker compose config

docker-restart: docker-down docker-up

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

docker-run-logger:
	docker compose run -it --rm --no-deps logger /bin/sh

docker-run-server:
	docker compose run -it --rm --no-deps server /bin/sh
