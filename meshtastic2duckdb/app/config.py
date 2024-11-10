import os

import dataclasses

@dataclasses.dataclass
class Config:
	db_filename      : str
	mode             : str
	print_stats_every: int
	debug            : bool
	trace            : bool

	@classmethod
	def load_env(cls):
		db_filename       = os.environ.get("MESH_LOGGER_DB_FILENAME"          , "meshtastic_logger.duckdb")
		mode              = os.environ.get("MESH_LOGGER_MODE"                 , "http")
		print_stats_every = os.environ.get("MESH_LOGGER_PRINT_STATS_EVERY"    , "60")
		debug             = os.environ.get("MESH_LOGGER_DEBUG"                , "false")
		trace             = os.environ.get("MESH_LOGGER_TRACE"                , "false")

		print_stats_every = int(print_stats_every)
		debug             = debug.lower()     in "1,t,y,true,yes".split(",")
		trace             = trace.lower()     in "1,t,y,true,yes".split(",")

		assert db_filename
		assert mode.lower() in "local,http".split(",")

		inst              = cls(
			db_filename       = db_filename,
			mode              = mode,
			print_stats_every = print_stats_every,
			debug             = debug,
			trace             = trace
		)

		print(f"db_filename      : {inst.db_filename}")
		print(f"mode             : {inst.mode}")
		print(f"print_stats_every: {inst.print_stats_every}")
		print(f"debug            : {inst.debug}")
		print(f"trace            : {inst.trace}")

		return inst

@dataclasses.dataclass
class ConfigLocal:
	memory_limit_mb  : int
	read_only        : bool
	pooled           : bool
	echo             : bool

	@classmethod
	def load_env(cls):
		memory_limit_mb   = os.environ.get("MESH_LOGGER_LOCAL_MEMORY_LIMIT_MB", "64")
		read_only         = os.environ.get("MESH_LOGGER_LOCAL_READ_ONLY"      , "false")
		pooled            = os.environ.get("MESH_LOGGER_LOCAL_POOLED"         , "true")
		echo              = os.environ.get("MESH_LOGGER_LOCAL_SQL_ECHO"       , "false")

		memory_limit_mb   = int(memory_limit_mb)
		read_only         = read_only.lower() in "1,t,y,true,yes".split(",")
		pooled            = pooled.lower()    in "1,t,y,true,yes".split(",")
		echo              = echo.lower()      in "1,t,y,true,yes".split(",")

		inst              = cls(
			memory_limit_mb = memory_limit_mb,
			read_only       = read_only,
			pooled          = pooled,
			echo            = echo
		)

		print(f"memory_limit_mb  : {inst.memory_limit_mb}")
		print(f"read_only        : {inst.read_only}")
		print(f"pooled           : {inst.pooled}")
		print(f"echo             : {inst.echo}")

		return inst

@dataclasses.dataclass
class ConfigRemoteHttp:
	proto   : str
	host    : str
	port    : int

	@classmethod
	def load_env(cls):
		proto             = os.environ.get("MESH_LOGGER_REMOTE_HTTP_PROTO"    , "http")
		host              = os.environ.get("MESH_LOGGER_REMOTE_HTTP_HOST"     , "127.0.0.1")
		port              = os.environ.get("MESH_LOGGER_REMOTE_HTTP_PORT"     , "8000")

		port              = int(port)

		assert proto.lower() in "http,https".split(",")

		#if host is not None:
		#	if host.lower() != "localhost":
		#		assert len(host.split(".")) == 4, f"invalid host: {host}"

		inst = cls(proto=proto, host=host, port=port)

		print(f"proto            : {inst.proto}")
		print(f"host             : {inst.host}")
		print(f"port             : {inst.port}")

		return inst

