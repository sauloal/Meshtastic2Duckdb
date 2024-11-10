#!/usr/bin/env python3

import logging
import typing as t

from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request, Response
from fastapi.staticfiles import StaticFiles

from . import models
from . import db





@asynccontextmanager
async def lifespan(app: FastAPI):
	# Load the ML model
	on_startup(app)
	yield
	# Clean up the ML models and release the resources
	on_cleanup(app)

def on_startup(app):
	#create_db_and_tables()
	pass

def on_cleanup(app):
	pass





# https://github.com/encode/starlette/issues/864
class EndpointFilter(logging.Filter):
	def __init__(
		self,
		path: str,
		*args: t.Any,
		**kwargs: t.Any,
	):
		super().__init__(*args, **kwargs)
		self._path = path

	def filter(self, record: logging.LogRecord) -> bool:
		return record.getMessage().find(self._path) == -1

uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(path="/livez"))
uvicorn_logger.addFilter(EndpointFilter(path="/readyz"))




app = FastAPI(
	docs_url  = "/api/docs",
	redoc_url = "/api/redoc",
	version   = "0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# https://jnikenoueba.medium.com/using-fastapi-with-sqlalchemy-5cd370473fe5
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-session-dependency
# https://donnypeeters.com/blog/fastapi-sqlalchemy/





@app.get("/")
async def root():
	return ""

@app.get("/livez")
async def livez():
	return ""

@app.get("/readyz")
async def readyz():
	return ""

@app.get("/api")
async def api_get():
	return { "endpoints": ["dbs"] }

@app.get("/api/dbs")
async def api_dbs_get():
	# TODO: list files
	return { "endpoints": ["meshtastic_logger.duckdb"] }

@app.get("/api/dbs/{db_name}")
async def api_db_get(db_name: str):
	return { "endpoints": ["models"] }

@app.get("/api/dbs/{db_name}/models")
async def api_db_models_get(db_name: str):
	# TODO: Get from database
	return { "endpoints": ["NodeInfo", "Nodes", "RangeTest", "Telemetry", "TextMessage"] }





async def api_model_get(  session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.SharedFilterQuery ) -> list:
	print("api_model_get", "session_manager", session_manager, "request", request, "response", response, "query_filter", query_filter)
	#https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes
	#heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
	return []

async def api_model_post( data, session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	# print("api_model_post", "data", data, type(data), "session_manager", session_manager, "request", request, "response", response)

	orm = models.class_to_ORM(data)
	# print("  orm", orm)

	with session_manager as session:
		session.add(orm)
		session.commit()
	# print("  STORED")

	return None





@app.get("/api/dbs/{db_name}/models/nodeinfo",
	summary              = "Get NodeInfo",
	description          = "Get NodeInfo instances",
	response_description = "List of NodeInfo",
	tags                 = ["NodeInfo"])
async def api_model_nodeinfo_get(  db_name: str,                                 session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.SharedFilterQuery ) -> list[models.NodeInfoClass]:
	return await api_model_get(                                                  session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/dbs/{db_name}/models/nodeinfo",
	summary              = "Add NodeInfo",
	description          = "Add NodeInfo instance",
	response_description = "None",
	tags                 = ["NodeInfo"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_nodeinfo_post( db_name: str,    data: models.NodeInfoClass,  session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(                    data=data,                   session_manager=session_manager,         request=request,  response=response )






@app.get("/api/dbs/{db_name}/models/nodes",
	summary              = "Get Nodes",
	description          = "Get Node instances",
	response_description = "List of Nodes",
	tags                 = ["Node"])
async def api_model_node_get(      db_name: str,                                 session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.SharedFilterQuery ) -> list[models.NodesClass]:
	return await api_model_get(                                                  session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/dbs/{db_name}/models/nodes",
	summary              = "Add Node",
	description          = "Add Node instance",
	response_description = "None",
	tags                 = ["Node"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_node_post(     db_name: str,    data: models.NodesClass,     session_manager: db.SessionManagerDepRW, request: Request, response: Response) -> None:
	return await api_model_post(                    data=data,                   session_manager=session_manager,         request=request,  response=response )





@app.get("/api/dbs/{db_name}/models/telemetry",
	summary="Get Telemetries",
	description="Get Telemetry instances",
	response_description="List of Telemetries",
	tags=["Telemetry"])
async def api_model_node_get(      db_name: str,                                 session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.SharedFilterQuery ) -> list[models.TelemetryClass]:
	return await api_model_get(                                                  session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/dbs/{db_name}/models/telemetry",
	summary="Add Telemetry",
	description="Add Telemetry instance",
	response_description="None",
	tags=["Telemetry"],
	status_code=status.HTTP_201_CREATED)
async def api_model_node_post(     db_name: str,    data: models.TelemetryClass, session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(                    data=data,                   session_manager=session_manager,         request=request,  response=response )



#https://fastapi.tiangolo.com/advanced/websockets/#in-production
#@app.websocket("/ws")
#async def websocket_endpoint(websocket: WebSocket):
#    await websocket.accept()
#    while True:
#        data = await websocket.receive_text()
#        await websocket.send_text(f"Message text was: {data}")






# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-bar-charts/
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-line-charts/
# https://github.com/bugbytes-io/django-htmx-bokeh/tree/barchart
