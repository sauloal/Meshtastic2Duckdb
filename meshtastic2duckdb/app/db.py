import sys
import typing
import requests
from functools import lru_cache

from typing import Annotated, Generator

from sqlalchemy.pool import NullPool

from fastapi import Depends

from sqlmodel import SQLModel, create_engine, Session

from .config     import Config, ConfigLocal, ConfigRemoteHttp
from .dbgenerics import GenericSession, GenericSessionManager, DbEngine
from .           import models

class DbEngineHTTP(DbEngine):
	def __init__(self, host: str, port: int, proto: str = "http", debug=False):
		self.host        = host
		self.port        = port
		self.proto       = proto
		self.debug       = debug

	@property
	def url(self) -> str:
		return f"{self.proto}://{self.host}:{self.port}"

	@property
	def url_add(self) -> str:
		return f"{self.url}/api/messages"

	def get_add_url(self, model_name: str) -> str:
		return f"{self.url_add}/{model_name.lower()}"

	def get_session_manager(self):
		return DbEngineHTTP.SessionManager(self)

	def post(self, instance) -> dict[str, int]:
		if self.debug: print("POSTING", instance)

		table_name = instance.__class__.__tablename__
		data       = instance.toDICT()
		url        = self.get_add_url(table_name)

		if self.debug:
			print("  TABLE", table_name)
			print("  DATA ", data)
			print("  URL  ", url)

		try:
			res        = requests.post(url, json = data)
		except requests.exceptions.ConnectionError as e:
			print(e, file=sys.stderr)
			print()
			return

		if self.debug:
			print("  RES  ", res)
			print("  RES  ", res.text)
			#print("  RES  ", res.request.body)
			print()

		return { table_name.upper(): 1 }

	class Session(GenericSession):
		def __init__(self, db_engine):
			self.db_engine = db_engine

		def add(self, instance) -> dict[str, int]:
			return self.db_engine.post(instance)

		def commit(self):
			pass

	class SessionManager(GenericSessionManager):
		def __init__(self, db_engine: "DbEngine"):
			self.db_engine = db_engine

		def __enter__(self) -> GenericSession:
			#print(f"  creating session")

			# TODO: THINK ON USING WEBSOCKET
			return DbEngineHTTP.Session(self.db_engine)

		def __exit__(self, type, value, traceback):
			#print(f"  closing session")
			pass

class DbEngineLocal(DbEngine):
	def __init__(self, db_filename: str, memory_limit_mb: int = 64, threads: int = 1, read_only: bool = False, pooled: bool = False, echo: bool = False, debug: bool = False):
		self.db_filename     = db_filename
		self.memory_limit_mb = memory_limit_mb
		self.read_only       = read_only
		self.echo            = echo
		self.debug           = debug
		self.engine          = None
		self.Base            = None

		print(f"creating SQLMODEL database")
		print(f"  creating engine")
		self.engine          = create_engine(
			f"duckdb:///dbs/{self.db_filename}",
			connect_args = {
				'read_only': self.read_only,
				'config': {
					'memory_limit': f'{memory_limit_mb}mb',
					'max_memory': f'{memory_limit_mb}mb',
					'threads'     : threads
				}
			},
			echo = echo,
			**({} if pooled else {"poolclass": NullPool})
		)

		print(f"  creating sequences")
		#self.Base.metadata.create_all(self.engine)
		for sequence in models.Sequences:
			#print("    sequence", sequence)
			try:
				sequence.create(self.engine, checkfirst=False)
			except:
				pass

		print(f"  creating tables")
		SQLModel.metadata.create_all(self.engine)

		print(f"  created")

	def __del__(self):
		if self.engine:
			self.engine.dispose()

	def get_session_manager(self) -> GenericSessionManager:
		return DbEngineLocal.SessionManager(self)

	class SessionManager(GenericSessionManager):
		def __init__(self, db_engine: "DbEngine"):
			self.db_engine = db_engine

		def __enter__(self) -> GenericSession:
			#print(f"  creating session")

			self.session = Session(bind=self.db_engine.engine)
			return self.session

		def __exit__(self, type, value, traceback):
			#print(f"  closing session")
			self.session.commit()
			self.session.close()
			del self.session





def dbEngineLocalFromConfig(*, config: Config, config_local: ConfigLocal) -> DbEngine:
	db_engine   = DbEngineLocal(
		db_filename     = config.db_filename,
		memory_limit_mb = config_local.memory_limit_mb,
		read_only       = config_local.read_only,
		pooled          = config_local.pooled,
		echo            = config_local.echo,
		debug           = config.debug
	)

	return db_engine

def dbEngineRemoteHttpFromConfig(*, config: Config, config_remote_http: ConfigRemoteHttp) -> DbEngine:
	db_engine   = DbEngineHTTP(
		proto           = config_remote_http.proto,
		host            = config_remote_http.host,
		port            = config_remote_http.port,
		debug           = config.debug
	)

	return db_engine





def dbEngineLocalFromEnv(*, overrides: dict[str, typing.Any] = None, verbose: bool = False) -> DbEngine:
	config              = Config     .load_env(overrides=overrides, verbose=verbose)
	config_local        = ConfigLocal.load_env(overrides=overrides, verbose=verbose)
	db_engine           = dbEngineLocalFromConfig(config=config, config_local=config_local)
	return db_engine

def dbEngineRemoteHttpFromEnv(*, overrides: dict[str, typing.Any] = None, verbose : bool = False) -> DbEngine:
	config              = Config          .load_env(overrides=overrides, verbose=verbose)
	config_remote_http  = ConfigRemoteHttp.load_env(overrides=overrides, verbose=verbose)
	db_engine           = dbEngineRemoteHttpFromConfig(config=config, config_remote_http=config_remote_http)
	return db_engine





class DbManager:
	def __init__(self, db_engine: DbEngine):
		self.num_messages = 0
		self.num_nodes    = 0
		self.num_adds     = 0
		self.class_stats  = {}
		self.db_engine    = db_engine

		# https://github.com/Mause/duckdb_engine
		# https://docs.sqlalchemy.org/en/20/orm/mapping_api.html

		# https://github.com/Mause/duckdb_engine
		# https://motherduck.com/docs/integrations/language-apis-and-drivers/python/sqlalchemy/
		# con = duckdb.connect(database = "my-db.duckdb", read_only = False)
		# con.execute("CREATE TABLE items (item VARCHAR, value DECIMAL(10, 2), count INTEGER)")
		# con.execute("INSERT INTO items VALUES ('jeans', 20.0, 1), ('hammer', 42.2, 2)")

	def __del__(self):
		del self.db_engine

	def decode_packet(self, packet):
		self.num_messages += 1
		return models.decode_packet(packet)

	def decode_nodes(self, nodes) -> list[models.Nodes]:
		instances       = models.decode_nodes(nodes)
		self.num_nodes += len(instances)
		return instances

	def add_instances(self, instances):
		res              = self.db_engine.add_instances(instances)
		self.num_adds   += len(instances)
		for k,v in res.items(): self.class_stats[k] = self.class_stats.get(k,0) + v

	@property
	def stats(self):
		return {
			**{
				(1, "num_messages"): self.num_messages,
				(1, "num_nodes"   ): self.num_nodes   ,
				(1, "num_adds"    ): self.num_adds
			},
			**{ (2, k): v for k,v in self.class_stats.items() }
		}




db_engine = None

@lru_cache(maxsize=None)
def get_engine():
	global db_engine
	if db_engine is None:
		print("DB GET_ENGINE")
		#db_engine   = DbEngineLocal(db_filename=db_name)
		db_engine   = dbEngineLocalFromEnv(verbose=False)

	print("DB GET_ENGINE", db_engine)
	return db_engine




# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-session-dependency
def get_session_manager(read_only:bool) -> Generator[GenericSessionManager, None, None]:
	engine = get_engine()
	with engine.get_session_manager() as session_manager:
		yield session_manager

def get_session_manager_readonly() -> Generator[GenericSessionManager, None, None]:
	for session_manager in get_session_manager(read_only=True):
		yield session_manager

def get_session_manager_readwrite() -> Generator[GenericSessionManager, None, None]:
	for session_manager in get_session_manager(read_only=False):
		yield session_manager

SessionManagerDepRO = Annotated[GenericSessionManager, Depends(get_session_manager_readonly )]
SessionManagerDepRW = Annotated[GenericSessionManager, Depends(get_session_manager_readwrite)]

