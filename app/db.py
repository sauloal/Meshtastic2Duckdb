import sys
import requests

from typing import Annotated, Generator

from sqlalchemy.pool        import NullPool

#from sqlalchemy import create_engine

from sqlmodel import SQLModel, create_engine, Session


from . import models


class GenericSession:
	def add(self, instance):
		raise NotImplementedError

	def commit(self):
		raise NotImplementedError

class GenericSessionManager:
	def __init__(self, db_engine: "DbEngine"):
		raise NotImplementedError

	def __enter__(self) -> GenericSession:
		raise NotImplementedError

	def __exit__(self, type, value, traceback):
		raise NotImplementedError




class DbEngine:
	def __int__():
		raise NotImplementedError

	def get_session_manager(self):
		raise NotImplementedError

	def add_instances(self, instances) -> dict[str, int]:
		stats = {}
		with self.get_session_manager() as session:
			for instance in instances:
				#print(instance, type(instance))
				session.add(instance)
				stats[instance.__class__.__tablename__] = stats.get(instance.__class__.__tablename__, 0) + 1
			session.commit()
		return stats

class DbEngineHTTP(DbEngine):
	def __init__(self, db_filename: str, host: str, port: int, proto: str = "http", debug=False):
		self.db_filename = db_filename
		self.host        = host
		self.port        = port
		self.proto       = proto
		self.debug       = debug

	@property
	def url(self) -> str:
		return f"{self.proto}://{self.host}:{self.port}"

	@property
	def url_add(self) -> str:
		return f"{self.url}/api/dbs/{self.db_filename}/models"

	def get_add_url(self, model_name: str) -> str:
		return f"{self.url_add}/{model_name.lower()}"

	def get_session_manager(self):
		return DbEngineHTTP.SessionManager(self)

	def post(self, instance):
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

	class Session(GenericSession):
		def __init__(self, db_engine):
			self.db_engine = db_engine

		def add(self, instance):
			self.db_engine.post(instance)

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
	def __init__(self, db_filename: str, memory_limit_mb: int = 500, read_only: bool = False, pooled: bool = False, echo: bool = False):
		self.db_filename     = db_filename
		self.memory_limit_mb = memory_limit_mb
		self.read_only       = read_only
		self.echo            = echo
		self.engine          = None
		self.Base            = None

		print(f"creating SQLMODEL database")
		print(f"  creating engine")
		self.engine          = create_engine(
			f"duckdb:///{self.db_filename}",
			connect_args = {
				'read_only': self.read_only,
				'config': {
					'memory_limit': f'{memory_limit_mb}mb'
				}
			},
			echo = echo,
			**({} if pooled else {"poolclass": NullPool})
		)

		print(f"  generating base")
		#self.Base = models.reg.generate_base()

		print(f"  creating all")
		#self.Base.metadata.create_all(self.engine)
		for sequence in models.Sequences:
			print("    sequence", sequence)
			try:
				sequence.create(self.engine, checkfirst=False)
			except:
				pass

		SQLModel.metadata.create_all(self.engine)

		print(f"  created")

	def __del__(self):
		if self.engine:
			self.engine.dispose()

	def get_session_manager(self):
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

	def decode_nodes(self, nodes):
		instances       = models.decode_nodes(nodes)
		self.num_nodes += len(instances)
		return instances

	def add_instances(self, instances):
		res              = self.db_engine.add_instances(instances)
		self.num_adds   += len(instances)
		self.class_stats = { k: self.class_stats.get(k,0) + v for k,v in res.items() }

	@property
	def stats(self):
		return {
			**{
				"num_messages": self.num_messages,
				"num_nodes"   : self.num_nodes   ,
				"num_adds"    : self.num_adds
			},
			**self.class_stats
		}





from functools import lru_cache
from typing import Annotated
from fastapi import Depends

@lru_cache(maxsize=None)
def get_engine(db_name: str):
	db_engine   = DbEngineLocal(db_filename=db_name)
	return db_engine


# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-session-dependency
def get_session_manager(db_name: str, read_only:bool) -> Generator[GenericSessionManager, None, None]:
	#with get_engine(db_name):
	#	yield db
	#	#db.close()
	#with self._session_manager() as session:
	engine = get_engine(db_name)
	with engine.get_session_manager() as session_manager:
		yield session_manager

def get_session_manager_readonly(db_name: str) -> Generator[GenericSessionManager, None, None]:
	for session_manager in get_session_manager(db_name, read_only=True):
		yield session_manager

def get_session_manager_readwrite(db_name: str) -> Generator[GenericSessionManager, None, None]:
	for session_manager in get_session_manager(db_name, read_only=False):
		yield session_manager

SessionManagerDepRO = Annotated[GenericSessionManager, Depends(get_session_manager_readonly )]
SessionManagerDepRW = Annotated[GenericSessionManager, Depends(get_session_manager_readwrite)]
