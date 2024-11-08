#!/usr/bin/env python3

from enum import Enum
from typing import Union
from typing import Annotated

from fastapi import FastAPI, status, Query, Depends, Request, Response
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field

app = FastAPI(
	docs_url  = "/api/docs",
	redoc_url = "/api/redoc",
	version   = "0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-bar-charts/
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-line-charts/
# https://github.com/bugbytes-io/django-htmx-bokeh/tree/barchart

class DBSession:
	def __enter__(self):
		return {"a":"b", "c":"d"}

	def __exit__(self, a, b, c):
		pass

# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-session-dependency
def get_session(read_only:bool):
	with DBSession() as db:
		yield db
		#db.close()

def get_session_readonly():
	for session in get_session(read_only=True):
		yield session

def get_session_readwrite(mode):
	for session in get_session(read_only=False):
		yield session

SessionDepRO = Annotated[DBSession, Depends(get_session_readonly )]
SessionDepRW = Annotated[DBSession, Depends(get_session_readwrite)]

class NodeInfo:
	pass
class Alexnet:
	pass
class Resnet:
	pass
class Lenet:
	pass

class ModelName(str, Enum):
	nodeinfo = NodeInfo
	alexnet  = Alexnet
	resnet   = Resnet
	lenet    = Lenet


# https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#classes-as-dependencies_1
class FilterQueryParams(BaseModel):
	offset : Annotated[int       , Query(default=0  , ge=0        )]
	limit  : Annotated[int       , Query(default=100, gt=0, le=100)]
	q      : Annotated[str | None, Query(default=None             )]
	#order_by: Literal["created_at", "updated_at"] = "created_at"
	#tags    : list[str] = []

FilterQuery = Annotated[FilterQueryParams, Depends(FilterQueryParams)]




@app.get("/")
async def root():
	return ""

@app.get("/api")
async def api_get():
	return { "endpoints": ["models"] }

@app.get("/api/models")
async def api_models_get():
	return { "endpoints": ["NodeInfo", "Nodes", "RangeTest", "Telemetry", "TextMessage"] }






async def api_model_get(  model_name: ModelName, session: SessionDepRO, request: Request, response: Response, query_filter: FilterQuery ):
	print("api_model_get", "model_name", model_name, type(model_name), "session", session, "request", request, "response", response, "query_filter", query_filter)
	#https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes
	#heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
	return []

async def api_model_post( model_name: ModelName, session: SessionDepRW, request: Request, response: Response ):
	print("api_model_post", "model_name", model_name, type(model_name), "session", session, "request", request, "response", response)
	#raise HTTPException(status_code=404, detail="Item not found")
	#return JSONResponse(
	#	status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
	#	content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
	#)
	return None





@app.get("/api/models/NodeInfo", summary="Get NodeInfo", description="Get NodeInfo instances", response_description="List of NodeInfo", tags=["NodeInfo"])
async def api_model_nodeinfo_get( session: SessionDepRO, request: Request, response: Response, query_filter: FilterQuery ) -> list[str]:
	return await api_model_get(  model_name=ModelName.nodeinfo, session=session, request=request, response=response, query_filter=query_filter  )

@app.post("/api/models/NodeInfo", summary="Add NodeInfo", description="Add NodeInfo instances", response_description="None", tags=["NodeInfo"], status_code=status.HTTP_201_CREATED)
async def api_model_nodeinfo_post( session: SessionDepRW, request: Request, response: Response ) -> None:
	return await api_model_post( model_name=ModelName.nodeinfo, session=session, request=request, response=response )



#https://fastapi.tiangolo.com/advanced/websockets/#in-production
#@app.websocket("/ws")
#async def websocket_endpoint(websocket: WebSocket):
#    await websocket.accept()
#    while True:
#        data = await websocket.receive_text()
#        await websocket.send_text(f"Message text was: {data}")

