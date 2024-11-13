
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
				stats[instance.__class__.__tablename__.upper()] = stats.get(instance.__class__.__tablename__.upper(), 0) + 1
			session.commit()
		return stats

