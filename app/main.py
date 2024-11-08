#!/usr/bin/env python3

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Query, Depends, Request, Response
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from . import models
from . db import SessionManagerDepRO, SessionManagerDepRW


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


app = FastAPI(
	docs_url  = "/api/docs",
	redoc_url = "/api/redoc",
	version   = "0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# https://jnikenoueba.medium.com/using-fastapi-with-sqlalchemy-5cd370473fe5
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-session-dependency
# https://donnypeeters.com/blog/fastapi-sqlalchemy/




# https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#classes-as-dependencies_1
class FilterQueryParams(BaseModel):
	offset : Annotated[int       , Query(default=0  , ge=0        )]
	limit  : Annotated[int       , Query(default=100, gt=0, le=100)]
	q      : Annotated[str | None, Query(default=None             )]
	#order_by: Literal["created_at", "updated_at"] = "created_at"
	#tags    : list[str] = []
	dryrun : Annotated[bool      , Query(default=False)]

FilterQuery = Annotated[FilterQueryParams, Depends(FilterQueryParams)]





@app.get("/")
async def root():
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






async def api_model_get(  db_name: str, session_manager: SessionManagerDepRO, request: Request, response: Response, query_filter: FilterQuery ):
	print("api_model_get", "session_manager", session_manager, "request", request, "response", response, "query_filter", query_filter)
	#https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes
	#heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
	return []

async def api_model_post( db_name: str, data, session_manager: SessionManagerDepRW, request: Request, response: Response ):
	# print("api_model_post", "data", data, type(data), "session_manager", session_manager, "request", request, "response", response)

	orm = models.class_to_ORM(data)
	# print("  orm", orm)

	with session_manager as session:
		session.add(orm)
		session.commit()
	# print("  STORED")

	#raise HTTPException(status_code=404, detail="Item not found")
	#return JSONResponse(
	#	status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
	#	content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
	#)

	return None




@app.get("/api/dbs/{db_name}/models/nodeinfo",
	summary              = "Get NodeInfo",
	description          = "Get NodeInfo instances",
	response_description = "List of NodeInfo",
	tags                 = ["NodeInfo"])
async def api_model_nodeinfo_get(  db_name: str,                                 session_manager: SessionManagerDepRO, request: Request, response: Response, query_filter: FilterQuery ) -> list[str]:
	return await api_model_get(    db_name=db_name,                              session_manager=session_manager,      request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/dbs/{db_name}/models/nodeinfo",
	summary              = "Add NodeInfo",
	description          = "Add NodeInfo instance",
	response_description = "None",
	tags                 = ["NodeInfo"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_nodeinfo_post( db_name: str,    data: models.NodeInfoClass,  session_manager: SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(   db_name=db_name, data=data,                   session_manager=session_manager,      request=request,  response=response )






@app.get("/api/dbs/{db_name}/models/nodes",
	summary              = "Get Nodes",
	description          = "Get Node instances",
	response_description = "List of Nodes",
	tags                 = ["Node"])
async def api_model_node_get(      db_name: str,                                 session_manager: SessionManagerDepRO, request: Request, response: Response, query_filter: FilterQuery ) -> list[str]:
	return await api_model_get(    db_name=db_name,                              session_manager=session_manager,      request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/dbs/{db_name}/models/nodes",
	summary              = "Add Node",
	description          = "Add Node instance",
	response_description = "None",
	tags                 = ["Node"],
	status_code          = status.HTTP_201_CREATED)
async def api_model_node_post(     db_name: str,    data: models.NodesClass,     session_manager: SessionManagerDepRW, request: Request, response: Response) -> None:
	return await api_model_post(   db_name=db_name, data=data,                   session_manager=session_manager,      request=request,  response=response )





@app.get("/api/dbs/{db_name}/models/telemetry",
	summary="Get Telemetries",
	description="Get Telemetry instances",
	response_description="List of Telemetries",
	tags=["Telemetry"])
async def api_model_node_get(      db_name: str,                                 session_manager: SessionManagerDepRO, request: Request, response: Response, query_filter: FilterQuery ) -> list[str]:
	return await api_model_get(    db_name=db_name,                              session_manager=session_manager,      request=request,  response=response,  query_filter=query_filter  )

@app.post("/api/dbs/{db_name}/models/telemetry",
	summary="Add Telemetry",
	description="Add Telemetry instance",
	response_description="None",
	tags=["Telemetry"],
	status_code=status.HTTP_201_CREATED)
async def api_model_node_post(     db_name: str,    data: models.TelemetryClass, session_manager: SessionManagerDepRW, request: Request, response: Response ) -> None:
	return await api_model_post(   db_name=db_name, data=data,                   session_manager=session_manager,      request=request,  response=response )



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
