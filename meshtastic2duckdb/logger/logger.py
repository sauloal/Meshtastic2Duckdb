import os
import time
import serial

import dataclasses

import meshtastic
import meshtastic.serial_interface

from pubsub import pub


from app import db

# https://python.meshtastic.org/#example-usage

def print_packet(packet, depth=0):
	if depth == 0:
		print( "========")

	for k,v in sorted(packet.items()):
		if k == "raw": continue
		if isinstance(v, dict):
			print(f"{' '*depth}{k}{' '*(24-depth-len(str(k)))}: {type(v)}")
			#print(f"{' '*depth}--------")
			print_packet(v, depth=depth+2)
		else:
			print(f"{' '*depth}{k}{' '*(24-depth-len(str(k)))}: {type(v)} {v}")
			#print(f"{' '*depth}--------")

	if depth == 0:
		print("-"*50)

def print_interface(interface):
	# https://python.meshtastic.org/serial_interface.html
	#longName   = interface.getLongName()
	#getMyNodeInfo
	#getMyUser
	#getPublicKey
	#getShortName
	#onResponsePosition(p)
	#onResponseTelemetry(p)
	#onResponseTraceRoute(p)

	nodes      = interface.nodes
	nodesByNum = interface.nodesByNum
	myInfo     = interface.myInfo
	"""
	my_node_num    : 24
	min_app_version: 30200
	"""
	metadata   = interface.metadata
	"""
	firmware_version    : "2.5.9.936260f"
	device_state_version: 23
	canShutdown         : true
	hasBluetooth        : true
	role                : TRACKER
	position_flags      : 811
	hw_model            : TRACKER_T1000_E
	hasPKC              : true
	"""

	localNode  = interface.localNode

	print("=" * 50)
	#print("nodes     ", type(nodes     ), nodes)
	print("nodes")
	print_packet(nodes)
	print("=" * 50)
	#print("nodesByNum", type(nodesByNum), nodesByNum)
	print("nodesByNum")
	print_packet(nodesByNum)
	print("=" * 50)
	print("myInfo    ", type(myInfo    ), myInfo    )
	print("=" * 50)
	print("metadata  ", type(metadata  ), metadata  )
	print("=" * 50)
	print("localNode ", type(localNode ), localNode )
	print("=" * 50)
	print("=" * 50)

class Subscribers:
	def __init__(
			self,
			db_manager  : db.DbManager,
			debug       : bool = False,
			trace       : bool = False
		):
		self.db_manager   = db_manager
		self.trace        = trace
		self.debug        = debug

		pub.subscribe(self.on_receive   , "meshtastic.receive")
		pub.subscribe(self.on_connection, "meshtastic.connection.established")

	def on_receive(self, packet, interface): # called when a packet arrives
		#print(f"Received:", packet, type(packet), repr(packet))

		if self.debug:
			print("-"*50)
			print(f"Received")

		if self.trace:
			print_packet(packet)

		message = self.db_manager.decode_packet(packet)

		if message:
			if self.debug:
				print(message)
			self.db_manager.add_instances([message])

	def on_connection(self, interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
		# defaults to broadcast, specify a destination ID if you wish
		#interface.sendText("hello mesh")
		pass

	def on_nodes(self, nodes):
		self.db_manager.add_instances(nodes)

@dataclasses.dataclass
class Config:
	mode             : str
	db_filename      : str
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

		return inst

def run_local(*, config: Config, config_local: ConfigLocal):
	print(f"db_filename      : {config.db_filename}")
	print(f"memory_limit_mb  : {config_local.memory_limit_mb}")
	print(f"read_only        : {config_local.read_only}")
	print(f"pooled           : {config_local.pooled}")
	print(f"echo             : {config_local.echo}")

	db_engine   = db.DbEngineLocal(
		db_filename     = config.db_filename,
		memory_limit_mb = config_local.memory_limit_mb,
		read_only       = config_local.read_only,
		pooled          = config_local.pooled,
		echo            = config_local.echo,
		debug           = config.debug
	)

	run(config, db_engine)

def run_remote_http(*, config: Config, config_remote_http: ConfigRemoteHttp):
	print(f"db_filename      : {config.db_filename}")
	print(f"proto            : {config_remote_http.proto}")
	print(f"host             : {config_remote_http.host}")
	print(f"port             : {config_remote_http.port}")

	db_engine   = db.DbEngineHTTP(
		db_filename = config.db_filename,
		proto       = config_remote_http.proto,
		host        = config_remote_http.host,
		port        = config_remote_http.port,
		debug       = config.debug
	)

	run(config=config, db_engine=db_engine)

def run(*, config: Config, db_engine: db.DbEngine):
	print(f"mode             : {config.mode}")
	print(f"print_stats_every: {config.print_stats_every}")
	print(f"debug            : {config.debug}")
	print(f"trace            : {config.trace}")

	db_manager  = db.DbManager(db_engine)

	subscribers = Subscribers(db_manager, debug=config.debug, trace=config.trace)

	# By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0

	# https://python.meshtastic.org/serial_interface.html
	interface   = meshtastic.serial_interface.SerialInterface()
	#print_interface(interface)

	loop_num = 0
	try:
		while True:
			if loop_num % config.print_stats_every == 0: # min 600 seconds = 10 minutes
				nodes    = db_manager.decode_nodes( interface.nodesByNum )
				if len(nodes) > 0:
					if config.debug:
						for node in nodes:
							print("+++++++++++")
							print(node)
						print("+++++++++++")

					subscribers.on_nodes(nodes)

					#print(f"{'loops':15s}: {loop_num:12,d}")
					#for k, v in db_manager.stats.items():
					#	print(f"{k:15s}: {v:12,d}")
					print( "".join(f"{k}: {v:12,d} | " for k, v in sorted({**db_manager.stats, **{'loops':loop_num}}.items())) )

			loop_num += 1
			time.sleep(1)
	except KeyboardInterrupt:
		interface.close()
	except Exception as e:
		raise e

def main():
	config                     = Config.load_env()

	if   config.mode == "local":
		local_config       = ConfigLocal.load_env()
		run_local(config=config, config_local=config_local)

	elif config.mode == "http":
		config_remote_http = ConfigRemoteHttp.load_env()
		run_remote_http(config=config, config_remote_http=config_remote_http)

	else:
		raise f"unknown mode: {config.mode}"

if __name__ == "__main__":
	main()
