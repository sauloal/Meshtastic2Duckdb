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
	@echo
	@echo "  curl-get"
	@echo "  curl-get-filter"
	@echo "  curl-post"
	@echo
	@echo "  sql-dump"
	@echo "  sql-schema"
	@echo
	@echo "  venv"
	@echo "  install"
	@echo
	@echo "  docker-build"
	@echo "  docker-config"
	@echo "  docker-restart"
	@echo "  docker-restart-logger"
	@echo "  docker-restart-server"
	@echo "  docker-up"
	@echo "  docker-up-logger"
	@echo "  docker-up-server"
	@echo "  docker-up-server-dev"
	@echo "  docker-down"
	@echo "  docker-logs"
	@echo "  docker-ps"
	@echo "  docker-run-logger"
	@echo "  docker-run-server"
	@echo
	@echo "  user-dump-adrian"
	@echo "  user-dump-saulo"
	@echo "  user-dump-maria"





.PHONY: local-config
.PHONY: logger
.PHONY: server server-dev openapi
.PHONY: curl-get curl-get-filter curl-post

local-config:
	@echo 'export `cat config.env`; export `envsubst < config.env`'

logger:
	. .venv/bin/activate && cd meshtastic2duckdb     && python3 -m logger.logger

server:
ifeq ($(MESH_APP_DEBUG),)
	. .venv/bin/activate && cd meshtastic2duckdb/app && fastapi run main.py --host="$${MESH_APP_HOST}" --port="$${MESH_APP_PORT}"
else
	. .venv/bin/activate && cd meshtastic2duckdb/app && fastapi dev main.py --host="$${MESH_APP_HOST}" --port="$${MESH_APP_PORT}"
endif

server-dev:
	. .venv/bin/activate && cd meshtastic2duckdb/app && fastapi dev main.py --host="$${MESH_APP_HOST}" --port="$${MESH_APP_PORT}"

openapi:
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/openapi.json" | jq -C | less -SR

curl-get:
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodeinfo/list" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/rangetest/list" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/telemetry/list" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/textmessage/list" | jq .

curl-get-filter:
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodeinfo/list?roles=TRACKER" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodeinfo/list?roles=MAMA" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodeinfo/list?roles=TRACKER,CLIENT" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodeinfo/list?roles=TRACKER,CLIENT,MAMA" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodeinfo/list?shortNames=AAA" | jq .

	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list?is_favorite=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list?has_location=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list?roles=TRACKER" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list?roles=MAMA" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list?roles=TRACKER,CLIENT" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes/list?roles=TRACKER,CLIENT,MAMA" | jq .

	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list?hasLocation=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list?minLatitudeI=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list?minLatitude=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list?minAltitude=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list?minPDOP=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/position/list?minGroundSpeed=0" | jq .

	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/telemetry/list?minBatteryLevel=10" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/telemetry/list?hasLux=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/telemetry/list?hasTemperature=1" | jq .

	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/textmessage/list?isPkiEncrypted=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/textmessage/list?channels=1" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/textmessage/list?channels=a" | jq .
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/textmessage/list?channels=1,2" | jq .

curl-post:
	. ./config.env && curl -v "$${MESH_LOGGER_REMOTE_HTTP_HOST}:$${MESH_LOGGER_REMOTE_HTTP_PORT}/api/messages/nodes?dry-run=true" \
		-H 'content-type: application/json' \
		-d '{"hopsAway": 0, "lastHeard": 1731060061, "num": 4175865308, "snr": 16.5, "isFavorite": null, "airUtilTx": 3.0786943, "batteryLevel": 75, "channelUtilization": 5.9116664, "uptimeSeconds": 176372, "voltage": 3.942, "altitude": null, "latitude": null, "latitudeI": null, "longitude": null, "longitudeI": null, "time": null, "hwModel": "TRACKER_T1000_E", "user_id": "f8e6a5dc", "longName": "Saulo", "macaddr": "/pf45qXc", "publicKey": "zd9XSkmI+ptPM6H+PlReOTL2d5iCW6S/YHe3cGbQen4=", "role": "TRACKER", "shortName": "SAAA", "id": null}'





.PHONY: sql-dump sql-schema

sql-dump:
	export TS=`date +%s` ; \
	. ./.venv/bin/activate && \
	. ./config.env && \
	echo .dump   | duckdb -readonly meshtastic2duckdb/app/dbs/$${MESH_LOGGER_DB_FILENAME} > /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	cat /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	rm  /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS}

sql-schema:
	export TS=`date +%s` ; \
	. ./.venv/bin/activate && \
	. ./config.env && \
	echo .schema | duckdb -readonly meshtastic2duckdb/app/dbs/$${MESH_LOGGER_DB_FILENAME} > /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	cat /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS} ; \
	rm  /tmp/$${MESH_LOGGER_DB_FILENAME}_$${TS}





.PHONY: venv install

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip3 install -r requirements.txt
	rm duckdb_cli-linux-aarch64.zip || true;
	wget https://github.com/duckdb/duckdb/releases/download/v1.1.3/duckdb_cli-linux-aarch64.zip
	unzip duckdb_cli-linux-aarch64.zip
	mv -v duckdb .venv/bin/
	rm duckdb_cli-linux-aarch64.zip





.PHONY: docker-build docker-config
.PHONY: docker-restart docker-restart-logger docker-restart-server
.PHONY: docker-up docker-up-logger docker-up-server docker-up-server-dev
.PHONY: docker-down docker-logs docker-ps
.PHONY: docker-run-logger docker-run-server

docker-build:
	docker compose build

docker-config:
	docker compose config


docker-restart: docker-down docker-up

docker-restart-logger:
	docker compose stop logger; docker compose rm logger; docker compose up -d logger

docker-restart-server:
	docker compose stop server; docker compose rm server; docker compose up -d server


docker-up:
	docker compose up -d

docker-up-logger:
	docker compose up -d --no-deps --remove-orphans logger

docker-up-server:
	docker compose up -d --no-deps --remove-orphans server

docker-up-server-dev:
	docker compose up -d --no-deps --remove-orphans server


docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps


docker-run-logger:
	docker compose run -it --rm --no-deps --volume ./meshtastic2duckdb:/data/meshtastic2duckdb --service-ports logger /bin/bash

docker-run-server:
	docker compose run -it --rm --no-deps --volume ./meshtastic2duckdb:/data/meshtastic2duckdb --service-ports server /bin/bash




.PHONY:user-dump user-dump-adrian user-dump-maria user-dump-saulo

ifneq ($(NODE),)
user-dump:
	meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --export-config   > nodes/${NODE}.yaml
	meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --info            > nodes/${NODE}.info
	meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --nodes           > nodes/${NODE}.nodes
	meshtastic --serial /dev/serial/by-id/usb-Seeed_Studio_T1000-E-BOOT_* --device-metadata > nodes/${NODE}.meta
endif

user-dump-adrian:
	NODE=adrian $(MAKE) user-dump

user-dump-maria:
	NODE=maria  $(MAKE) user-dump

user-dump-saulo:
	NODE=saulo  $(MAKE) user-dump
