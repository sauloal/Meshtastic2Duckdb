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
async def livez() -> None:
	return None

@app.get("/readyz", response_class=HTMLResponse, status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def readyz() -> None:
	return None

@app.get("/api")
async def api_get() -> dict[str, list[str]]:
	return { "endpoints": ["messages"] }

@app.get("/api/messages")
async def api_models_get() -> dict[str, list[str]]:
	# TODO: Get from database
	return { "endpoints": ["nodeinfo", "nodes", "position", "rangetest", "telemetry", "textmessage"] }





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

	def mod_filter_key(filter_query, filter_key:str, filter_is_list:bool, path_param: str):
		if filter_key is not None:
			assert hasattr(filter_query, filter_key), f"query_filter '{query_filter}' does not have filter_key '{filter_key}': {dir(query_filter)}. {query_filter.model_fields}"

			if filter_is_list:
				setattr(filter_query, filter_key, [path_param])
			else:
				setattr(filter_query, filter_key,  path_param)

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

				mod_filter_key(filter_query=query_filter, filter_key=filter_key, filter_is_list=filter_is_list, path_param=path_param)

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

models.NodeInfo   .register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
models.Nodes      .register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
models.Position   .register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
models.RangeTest  .register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
models.Telemetry  .register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
models.TextMessage.register(prefix="/api/messages", gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)





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
