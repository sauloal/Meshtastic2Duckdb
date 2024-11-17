#!/usr/bin/env python3

import logging
import typing as t

from contextlib import asynccontextmanager

from fastapi             import FastAPI, status, Request, Response, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses   import HTMLResponse

from . import db
from . import htmx
from . import models




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



models.register(app, prefix="/api/messages", status=status, db=db)
htmx  .register(app, prefix="/mx"          , status=status)



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
