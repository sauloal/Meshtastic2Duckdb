#!/usr/bin/env python3

import logging
import typing as t

from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

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
# https://github.com/encode/starlette/blob/master/starlette/status.py


print("CONNECTING ENGINE")
db_engine   = db.dbEngineLocalFromEnv(verbose=False)
print(db_engine, type(db_engine))
print("ENGINE CONNECTED")


def get_engine():
	#print("APP GET_ENGINE")
	global db_engine
	#print("APP GET_ENGINE", db_engine)
	return db_engine

db.get_engine = get_engine



@app.get("/",       response_class=HTMLResponse, status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def root():
	return ""

@app.get("/livez",  response_class=HTMLResponse, status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def livez():
	return ""

@app.get("/readyz", response_class=HTMLResponse, status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def readyz():
	return ""

@app.get("/api")
async def api_get():
	return { "endpoints": ["messages"] }

@app.get("/api/messages")
async def api_models_get():
	# TODO: Get from database
	return { "endpoints": ["NodeInfo", "Nodes", "RangeTest", "Telemetry", "TextMessage"] }





async def api_model_get( model: models.Message,      session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.SharedFilterQuery ) -> list:
	#print("api_model_get", "model", model, "session_manager", session_manager, "request", request, "response", response, "query_filter", query_filter)
	#https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes

	resp = model.Query(session_manager=session_manager, query_filter=query_filter)

	return resp

async def api_model_post( data: models.MessageClass, session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	# print("api_model_post", "data", data, type(data), "session_manager", session_manager, "request", request, "response", response)

	orm = data.toORM()
	#orm = models.class_to_ORM(data)
	# print("  orm", orm)

	with session_manager as session:
		session.add(orm)
		session.commit()
	# print("  STORED")

	return None





@app.get("/api/messages/nodeinfo",
	summary              = "Get NodeInfo",
	description          = "Get NodeInfo instances",
	response_description = "List of NodeInfo",
	tags                 = ["NodeInfo"])
async def api_model_nodeinfo_get(                                  session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
	return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/messages/nodeinfo",
	summary              = "Add NodeInfo",
	description          = "Add NodeInfo instance",
	response_description = "None",
	tags                 = ["NodeInfo"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_nodeinfo_post(  data: models.NodeInfoClass,    session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,         request=request,  response=response )






@app.get("/api/messages/nodes",
	summary              = "Get Nodes",
	description          = "Get Node instances",
	response_description = "List of Nodes",
	tags                 = ["Node"])
async def api_model_node_get(                                      session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.Nodes.__filter__() ) -> list[models.NodesClass]:
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/messages/nodes",
	summary              = "Add Node",
	description          = "Add Node instance",
	response_description = "None",
	tags                 = ["Node"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_node_post(      data: models.NodesClass,       session_manager: db.SessionManagerDepRW, request: Request, response: Response) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,         request=request,  response=response )





@app.get("/api/messages/position",
	summary="Get Positions",
	description="Get Position instances",
	response_description="List of Positions",
	tags=["Position"])
async def api_model_position_get(                                  session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.Position.__filter__() ) -> list[models.PositionClass]:
	return await api_model_get( model=models.Position,         session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/messages/position",
	summary="Add Positions",
	description="Add Position instance",
	response_description="None",
	tags=["Position"],
	status_code=status.HTTP_201_CREATED)
async def api_model_position_post(  data: models.PositionClass,    session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,         request=request,  response=response )





@app.get("/api/messages/rangetest",
	summary              = "Get RangeTests",
	description          = "Get RangeTest instances",
	response_description = "List of RangeTests",
	tags                 = ["RangeTest"])
async def api_model_position_get(                                  session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.RangeTest.__filter__() ) -> list[models.RangeTestClass]:
	return await api_model_get( model=models.RangeTest,        session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/messages/rangetest",
	summary              = "Add RangeTests",
	description          = "Add RangeTest instance",
	response_description = "None",
	tags                 = ["RangeTest"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_position_post(  data: models.RangeTestClass,   session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,         request=request,  response=response )





@app.get("/api/messages/telemetry",
	summary              = "Get Telemetries",
	description          = "Get Telemetry instances",
	response_description = "List of Telemetries",
	tags                 = ["Telemetry"])
async def api_model_node_get(                                      session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.Telemetry.__filter__() ) -> list[models.TelemetryClass]:
	return await api_model_get( model=models.Telemetry,        session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/messages/telemetry",
	summary              = "Add Telemetry",
	description          = "Add Telemetry instance",
	response_description = "None",
	tags                 = ["Telemetry"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_node_post(      data: models.TelemetryClass,   session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,         request=request,  response=response )





@app.get("/api/messages/textmessage",
	summary              = "Get TextMessages",
	description          = "Get TextMessage instances",
	response_description = "List of TextMessages",
	tags                 = ["TextMessage"])
async def api_model_node_get(                                      session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.TextMessage.__filter__() ) -> list[models.TextMessageClass]:
	return await api_model_get( model=models.TextMessage,      session_manager=session_manager,         request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/messages/textmessage",
	summary              = "Add TextMessages",
	description          = "Add TextMessage instance",
	response_description = "None",
	tags                 = ["TextMessage"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_node_post(      data: models.TextMessageClass, session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,         request=request,  response=response )



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
