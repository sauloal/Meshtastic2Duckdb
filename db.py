import sys
import requests

from sqlalchemy.orm         import registry
from sqlalchemy.orm.session import Session
from sqlalchemy.pool        import NullPool

from sqlalchemy import create_engine

import models


class GenericSession:
	def add(self, instance):
		raise NotImplementedError

	def commit(self):
		raise NotImplementedError





class DbEngine:
	def __int__():
		raise NotImplementedError

	def add_instances(self, instances) -> dict[str, int]:
		stats = {}
		with self._session_manager() as session:
			for instance in instances:
				session.add(instance)
				stats[instance.__class__.__tablename__] = stats.get(instance.__class__.__tablename__, 0) + 1
			session.commit()
		return stats

class DbEngineHTTP(DbEngine):
	def __init__(self, host: str, port: int, proto: str = "http"):
		self.host  = host
		self.port  = port
		self.proto = proto

	@property
	def url(self) -> str:
		return f"{self.proto}://{self.host}:{self.port}"

	@property
	def url_add(self) -> str:
		return f"{self.url}/api/models"

	def get_add_url(self, model_name: str) -> str:
		return f"{self.url_add}/{model_name}"

	def _session_manager(self):
		return DbEngineHTTP.SessionManager(self)

	def post(self, instance):
		print("POSTING", instance)
		table_name = instance.__class__.__tablename__
		data       = instance.toJSON()
		url        = self.get_add_url(table_name)

		print("  TABLE", table_name)
		print("  DATA ", data)
		print("  URL  ", url)

		try:
			res        = requests.post(url, json = data)
		except requests.exceptions.ConnectionError as e:
			print(e, file=sys.stderr)
			print()
			return

		print("  RES  ", res)
		print()

	class Session(GenericSession):
		def __init__(self, db_engine):
			self.db_engine = db_engine

		def add(self, instance):
			self.db_engine.post(instance)

		def commit(self):
			pass

	class SessionManager:
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
	def __init__(self, filename: str, memory_limit_mb: int = 500, read_only: bool = False, pooled: bool = False):
		self.filename        = filename
		self.memory_limit_mb = memory_limit_mb
		self.read_only       = read_only
		self.engine          = None
		self.Base            = None

		print(f"creating database")
		print(f"  creating engine")
		self.engine          = create_engine(
			f"duckdb:///{self.filename}",
			connect_args = {
				'read_only': self.read_only,
				'config': {
					'memory_limit': f'{memory_limit_mb}mb'
				}
			},
			**({} if pooled else {"poolclass": NullPool})
		)

		print(f"  generating base")
		self.Base = models.reg.generate_base()

		print(f"  creating all")
		self.Base.metadata.create_all(self.engine)

	def __del__(self):
		if self.engine:
			self.engine.dispose()

	def _session_manager(self):
		return DbEngineLocal.SessionManager(self)

	class SessionManager:
		def __init__(self, db_engine: "DbEngine"):
			self.db_engine = db_engine

		def __enter__(self) -> GenericSession:
			#print(f"  creating session")

			self.session = Session(bind=self.db_engine.engine)
			return self.session

		def __exit__(self, type, value, traceback):
			#print(f"  closing session")
			self.session.close()










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
		return models.Message.from_packet_decoded(packet)

	def decode_nodes(self, nodes):
		instances = models.Nodes.from_nodes(nodes)
		self.num_nodes += len(instances)
		return instances

	def add_instances(self, instances):
		res = self.db_engine.add_instances(instances)
		self.num_adds += len(instances)
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
