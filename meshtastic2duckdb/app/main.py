#!/usr/bin/env python3

import logging
import typing as t

from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request, Response, Path
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





async def api_model_get( model: models.Message,      session_manager: db.SessionManagerDepRO, request: Request, response: Response, query_filter: models.SharedFilterQuery ) -> list[ models.Message]:
	#print("api_model_get", "model", model, "session_manager", session_manager, "request", request, "response", response, "query_filter", query_filter)
	#https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes

	resp = model.Query(session_manager=session_manager, query_filter=query_filter)

	return resp

async def api_model_post( data: models.MessageClass, session_manager: db.SessionManagerDepRW, request: Request, response: Response ) -> None:
	#print("api_model_post", "data", data, type(data), "session_manager", session_manager, "request", request, "response", response)
	#print(dir(data))

	orm = data.toORM()
	#orm = models.class_to_ORM(data)
	# print("  orm", orm)

	with session_manager as session:
		session.add(orm)
		session.commit()
	# print("  STORED")

	return None



def gen_endpoint(*, verb: str, endpoint: str, name: str, summary: str, description: str, model: models.Message, session_manager_t, tags: list[str], filter_key:str=None, filter_is_list: bool=False, response_model=None, fixed_response=None, status_code=None):
	assert verb in ("GET","POST")
	alias        = None
	data_class   = model.__dataclass__()
	query_filter = model.__filter__()

	operation_id = f"{endpoint}_{verb}".lower().replace("/","_").replace("{","_").replace("}","_").replace(":","_").replace("-","_").replace("__","_").strip("_")
	#print(f"  operation_id {operation_id}")

	if "{" in endpoint:
		alias = endpoint.split("{")[1].split("}")[0]
		#print(f"  ALIAS {alias}")

	if fixed_response is not None:
		assert verb == "GET"

	def mod_filter_key(filter_key:str = None, filter_is_list:bool = False, path_param: str = None):
		if   filter_key is not None:
			assert hasattr(query_filter, filter_key)

			if filter_is_list:
				setattr(query_filter, filter_key, [path_param])
			else:
				setattr(query_filter, filter_key,  path_param)

	if verb == "GET":
		if alias is not None:
			@app.get(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)
			async def endpoint(                             session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter, path_param: str = Path(alias=alias)) -> response_model:
				if fixed_response:
					return fixed_response

				mod_filter_key(filter_key=filter_key, filter_is_list=filter_is_list, path_param=path_param)

				return await api_model_get(model=model, session_manager=session_manager,    request=request,  response=response, query_filter=query_filter)

		else:
			@app.get(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)
			async def endpoint(                             session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter) -> response_model:
				if fixed_response:
					return fixed_response

				return await api_model_get(model=model, session_manager=session_manager,    request=request,  response=response, query_filter=query_filter)

	elif verb == "POST":
		if alias is not None:
			@app.post(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)

			async def endpoint(                 data: data_class, session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter,  path_param: str = Path(alias=alias)) -> response_model:
				return await api_model_post(data=data  , session_manager=session_manager,    request=request,  response=response, path_param=path_param)

		else:
			@app.post(
				endpoint,
				name           = name,
				summary        = summary,
				description    = description,
				tags           = tags,
				operation_id   = operation_id,
				response_model = response_model,
				status_code    = status_code
			)

			async def endpoint(                 data: data_class, session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter) -> response_model:
				return await api_model_post(data=data  , session_manager=session_manager,    request=request,  response=response)

	return endpoint

models.NodeInfo.register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
models.Nodes   .register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)




"""
@app.get( "/api/messages/nodes",                                   summary = "Get Nodes Endpoints",          description = "Get Nodes Endpoints",       response_description = "Nodes Endpoints",       tags = ["Nodes"])
async def api_model_nodes_get():
	return { "endpoints": ["list", "by-is-favorite", "by-user-id", "by-short-name", "by-long-name", "by-role", "by-has-location"] }

@app.post("/api/messages/nodes",                                   summary = "Add Nodes Instances",          description = "Add Nodes Instances",       response_description = "None",                  tags = ["Nodes"],       status_code = status.HTTP_201_CREATED)
async def api_model_nodes_post(     data: models.NodesClass,       session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/nodes/list",                              summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_list(                                    session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodesClass]:
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-user-id/{user_id}",              summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_user_id(user_id: str,                 session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.userIds = [user_id]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-long-name/{long_name}",          summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_long_name(long_name: str,             session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.longNames = [long_name]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-short-name/{short_name}",        summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_short_name(short_name: str,           session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.shortNames = [short_name]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-role/{role}",                    summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_role(role: str,                       session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.roles = [role]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-is-favorite/{favorite}",         summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_is_favorite(favorite: bool,           session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.isFavorite = favorite
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-has-location/{has-location}",    summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_has_location(has_location: bool,      session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.hasLocation = has_location
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )
"""




@app.get( "/api/messages/position",                                summary = "Get Position Endpoints",       description = "Get Position Endpoints",    response_description = "Position Endpoints",    tags = ["Position"])
async def api_model_position_get():
	return { "endpoints": ["list", "by-has-location"] }

@app.post("/api/messages/position",                                summary = "Add Position Instance",        description = "Add Position Instances",    response_description = "None",                  tags = ["Position"],    status_code = status.HTTP_201_CREATED)
async def api_model_position_post(  data: models.PositionClass,    session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/position/list",                           summary = "Get Position Instances",       description = "Get Position Instances",    response_description = "List of Position",      tags = ["Position"])
async def api_model_position_list(                                 session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Position.__filter__() ) -> list[models.PositionClass]:
	return await api_model_get( model=models.Position,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/position/by-has-location/{has-location}", summary = "Get Position Instances",       description = "Get Position Instances",    response_description = "List of Position",      tags = ["Position"])
async def api_model_position_by_has_location(has_location: bool,   session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Position.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.hasLocation = has_location
	return await api_model_get( model=models.Position,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )





@app.get( "/api/messages/rangetest",                               summary = "Get RangeTests Endpoints",     description = "Get RangeTests Endpoints",  response_description = "RangeTests Endpoints",  tags = ["RangeTests"])
async def api_model_rangetest():
	return { "endpoints": ["list"] }

@app.post("/api/messages/rangetest",                               summary = "Add RangeTests Instance",      description = "Add RangeTests Instances",  response_description = "None",                  tags = ["RangeTests"],  status_code = status.HTTP_201_CREATED)
async def api_model_rangetest_post( data: models.RangeTestClass,   session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/rangetest/list",                          summary = "Get RangeTests Instances",     description = "Get RangeTests Instances",  response_description = "List of RangeTests",    tags = ["RangeTests"])
async def api_model_rangetest_list(                                session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.RangeTest.__filter__() ) -> list[models.RangeTestClass]:
	return await api_model_get( model=models.RangeTest,        session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )





@app.get( "/api/messages/telemetry",                               summary = "Get Telemetry Endpoints",      description = "Get Telemetry Endpoints",   response_description = "Telemetry Endpoints",   tags = ["Telemetry"])
async def api_model_telemetry_get():
	return { "endpoints": ["list"] }

@app.post("/api/messages/telemetry",                               summary = "Add Telemetry Instance",       description = "Add Telemetry Instances",   response_description = "None",                  tags = ["Telemetry"],   status_code = status.HTTP_201_CREATED)
async def api_model_telemetry_post( data: models.TelemetryClass,   session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/telemetry/list",                          summary = "Get Telemetry Instances",      description = "Get Telemetry Instances",   response_description = "List of Telemetry",     tags = ["Telemetry"])
async def api_model_telemetry_list(                                session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Telemetry.__filter__() ) -> list[models.TelemetryClass]:
	return await api_model_get( model=models.Telemetry,        session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )





@app.get( "/api/messages/textmessage",                              summary = "Get TextMessage Endpoints",   description = "Get TextMessage Endpoints", response_description = "TextMessage Endpoints", tags = ["TextMessage"])
async def api_model_textmessage_get():
	return { "endpoints": ["list"] }

@app.post("/api/messages/textmessage",                              summary = "Add TextMessage Instance" ,   description = "Add TextMessage Instances", response_description = "None"                 , tags = ["TextMessage"], status_code = status.HTTP_201_CREATED)
async def api_model_textmessage_post(data: models.TextMessageClass, session_manager: db.SessionManagerDepRW, request: Request,                          response: Response ) -> None:
	return await api_model_post( data=data,                     session_manager=session_manager,         request=request,                           response=response )

@app.get( "/api/messages/textmessage/list",                         summary = "Get TextMessage Instances",   description = "Get TextMessage Instances", response_description = "List of TextMessage"  , tags = ["TextMessage"])
async def api_model_textmessage_list(                               session_manager: db.SessionManagerDepRO, request: Request,                          response: Response,     query_filter: models.TextMessage.__filter__() ) -> list[models.TextMessageClass]:
	return await api_model_get( model=models.TextMessage,       session_manager=session_manager,         request=request,                           response=response,      query_filter=query_filter  )



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
