import os
import time
import serial

import meshtastic
import meshtastic.serial_interface

from pubsub import pub

from app import db
from app.config import Config, ConfigLocal, ConfigRemoteHttp

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

def run_local(*, config: Config, config_local: ConfigLocal):
	db_engine   = db.dbEngineLocalFromConfig(config=config, config_local=config_local)

	run(config=config, db_engine=db_engine)

def run_remote_http(*, config: Config, config_remote_http: ConfigRemoteHttp):
	db_engine = db.dbEngineRemoteHttpFromConfig(config=config, config_remote_http=config_remote_http)

	run(config=config, db_engine=db_engine)

def run(*, config: Config, db_engine: db.DbEngine):
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
					print( "".join(f"{k[1]}: {v:12,d} | " for k, v in sorted({**db_manager.stats, **{(0,'loops'):loop_num}}.items())) )

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
