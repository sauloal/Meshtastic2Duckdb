import sys
import json
import typing
import dataclasses

from typing import Annotated

from sqlalchemy             import BigInteger, SmallInteger, Integer
from sqlalchemy.orm         import Mapped
from sqlalchemy.orm         import mapped_column
from sqlalchemy.orm         import registry

from sqlalchemy import Sequence

# https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html

#https://www.postgresql.org/docs/current/datatype-numeric.html
#smallint  2 bytes  small-range integer	                      -32768 to               +32767
#integer   4 bytes  typical choice for integer 	         -2147483648 to          +2147483647
#bigint    8 bytes  large-range integer	        -9223372036854775808 to +9223372036854775807

#intpk = Annotated[int, mapped_column(init=False, primary_key=True)]
int8  = Annotated[int, SmallInteger]
int16 = Annotated[int, SmallInteger]
int32 = Annotated[int, Integer     ]
int64 = Annotated[int, BigInteger  ]

# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapping-multiple-type-configurations-to-python-types
reg = registry(
	type_annotation_map = {
		int8 : SmallInteger(), # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.SMALLINT
		int16: SmallInteger(),
		int32: Integer()     , # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.INT
		int64: BigInteger()    # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.BIGINT
	}
)



@dataclasses.dataclass
class Fields:
	_shared_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = []
	_fields       : typing.ClassVar[list[tuple[str, typing.Callable]]] = []

	@classmethod
	def _parse_fields(cls, packet):
		try:
			return { k: v(packet) for k,v in cls._shared_fields + cls._fields }
		except KeyError as e:
			print(packet)
			raise e

	@classmethod
	def from_packet(cls, packet):
		fields  = cls._parse_fields(packet)

		try:
			inst    = cls(**fields)
		except Exception as e:
			print("cls           ", cls               , file=sys.stderr)
			print("fields        ", fields            , file=sys.stderr)
			print("_shared_fields", cls._shared_fields, file=sys.stderr)
			print("_fields       ", cls._fields       , file=sys.stderr)
			print("packet        ", packet            , file=sys.stderr)
			raise e

		return inst

	def toJSON(self) -> str:
		d = dataclasses.asdict(self)
		j = json.dumps(d)
		return j


@dataclasses.dataclass
class Message(Fields):
	from_node : Mapped[int64]
	to_node   : Mapped[int64]

	fromId    : Mapped[str   | None]
	toId      : Mapped[str]

	rxTime    : Mapped[int64]
	rxRssi    : Mapped[int16 | None]
	rxSnr     : Mapped[float | None]

	hopStart  : Mapped[int8  | None]
	hopLimit  : Mapped[int8  | None]

	message_id: Mapped[int64]
	priority  : Mapped[str   | None]

	portnum   : Mapped[str]
	bitfield  : Mapped[int8  | None]

	_shared_fields = [
		["from_node"  , lambda packet: packet["from"]                         ],
		["to_node"    , lambda packet: packet["to"]                           ],

		["fromId"     , lambda packet: packet["fromId"]                       ],
		["toId"       , lambda packet: packet["toId"]                         ],

		["rxTime"     , lambda packet: packet["rxTime"]                       ],
		["rxRssi"     , lambda packet: packet.get("rxRssi"  , None)           ],
		["rxSnr"      , lambda packet: packet.get("rxSnr"   , None)           ],

		["hopStart"   , lambda packet: packet.get("hopStart", None)           ],
		["hopLimit"   , lambda packet: packet.get("hopLimit", None)           ],

		["message_id" , lambda packet: packet["id"]                           ],
		["priority"   , lambda packet: packet.get("priority", None)           ],

		["portnum"    , lambda packet: packet["decoded"]["portnum"]           ],
		["bitfield"   , lambda packet: packet["decoded"].get("bitfield", None)],
	]

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = []

	@classmethod
	def from_packet_decoded(cls, packet) -> "Telemetry|NodeInfo|Position|TextMessage|RangeTest":
		message = Message.from_packet(packet)
		if   message.portnum == "TELEMETRY_APP":
			return Telemetry.from_packet(packet)
		elif message.portnum == "NODEINFO_APP":
			return NodeInfo.from_packet(packet)
		elif message.portnum == "POSITION_APP":
			return Position.from_packet(packet)
		elif message.portnum == "TEXT_MESSAGE_APP":
			return TextMessage.from_packet(packet)
		elif message.portnum == "RANGE_TEST_APP":
			return RangeTest.from_packet(packet)
		else:
			raise ValueError(f"Unknown portnum {message.portnum}. {packet}")





telemetry_id_seq = Sequence("Telemetry_id_seq")

@reg.mapped_as_dataclass
class Telemetry(Message):
	__tablename__ = "Telemetry"

	time              : Mapped[int64]
	batteryLevel      : Mapped[int8  | None] # 76
	voltage           : Mapped[float | None] # 3.956
	channelUtilization: Mapped[float | None] # 5.8016667
	airUtilTx         : Mapped[float | None] # 4.323389
	uptimeSeconds     : Mapped[int32 | None] # 51470
	numPacketsTx      : Mapped[int32 | None] # 62
	numPacketsRx      : Mapped[int32 | None] # 103
	numOnlineNodes    : Mapped[int16 | None] # 3
	numTotalNodes     : Mapped[int16 | None] # 3
	lux               : Mapped[float | None] # 0.0
	temperature       : Mapped[float | None] # 25.240046

	id                : Mapped[int64] = mapped_column(BigInteger, telemetry_id_seq, server_default=telemetry_id_seq.next_value(), primary_key=True, init=False)

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["time"               , lambda packet: packet["decoded"]["telemetry"]["time"]                                                ],
		["batteryLevel"       , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("batteryLevel"      , None)],
		["voltage"            , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("voltage"           , None)],
		["channelUtilization" , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("channelUtilization", None)],
		["airUtilTx"          , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("airUtilTx"         , None)],

		["uptimeSeconds"      , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("uptimeSeconds"     , None)],

		["numPacketsTx"       , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("numPacketsTx"      , None)],
		["numPacketsRx"       , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("numPacketsRx"      , None)],
		["numOnlineNodes"     , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("numOnlineNodes"    , None)],
		["numTotalNodes"      , lambda packet: packet["decoded"]["telemetry"].get("deviceMetrics"     ,{}).get("numTotalNodes"     , None)],

		["lux"                , lambda packet: packet["decoded"]["telemetry"].get("environmentMetrics",{}).get("lux"               , None)],
		["temperature"        , lambda packet: packet["decoded"]["telemetry"].get("environmentMetrics",{}).get("temperature"       , None)],
	]

"""
--------------------------------------------------
Received
========
from                    : <class 'int'> 24
to                      : <class 'int'> 42
decoded                 : <class 'dict'>
  portnum               : <class 'str'> TELEMETRY_APP
  payload               : <class 'bytes'> b'\r'
  bitfield              : <class 'int'> 0
  telemetry             : <class 'dict'>
    time                : <class 'int'> 17
    deviceMetrics       : <class 'dict'>
      batteryLevel      : <class 'int'> 76
      voltage           : <class 'float'> 3.956
      channelUtilization: <class 'float'> 5.8016667
      airUtilTx         : <class 'float'> 4.323389
      uptimeSeconds     : <class 'int'> 51470
      numPacketsTx      : <class 'int'> 62
      numPacketsRx      : <class 'int'> 103
      numOnlineNodes    : <class 'int'> 3
      numTotalNodes     : <class 'int'> 3
      lux               : <class 'float'> 0.0
      temperature       : <class 'float'> 25.240046
id                      : <class 'int'> 118
rxTime                  : <class 'int'> 17
rxSnr                   : <class 'float'> 13.0
rxRssi                  : <class 'int'> -37
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
priority                : <class 'str'> BACKGROUND
fromId                  : <class 'str'> !8f
toId                    : <class 'str'> ^all
--------------------------------------------------



Received
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'\r`N+g'
  portnum               : <class 'str'> TELEMETRY_APP
  telemetry             : <class 'dict'>
    deviceMetrics       : <class 'dict'>
      airUtilTx         : <class 'float'> 4.877611
      batteryLevel      : <class 'int'> 75
      channelUtilization: <class 'float'> 13.023334
      uptimeSeconds     : <class 'int'> 52370
      voltage           : <class 'float'> 3.948
    time                : <class 'int'> 360
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 281
priority                : <class 'str'> BACKGROUND
rxRssi                  : <class 'int'> -12
rxSnr                   : <class 'float'> 16.5
rxTime                  : <class 'int'> 364
to                      : <class 'int'> 42
toId                    : <class 'str'> ^all
"""





nodeinfo_id_seq = Sequence("NodeInfo_id_seq")

@reg.mapped_as_dataclass
class NodeInfo(Message):
	__tablename__ = "NodeInfo"

	user_id   : Mapped[str] # !a
	longName  : Mapped[str] # M
	shortName : Mapped[str] # M
	macaddr   : Mapped[str] # 8Z
	hwModel   : Mapped[str] # TRACKER_T1000_E
	role      : Mapped[str] # TRACKER
	publicKey : Mapped[str] # S3

	id        : Mapped[int64] = mapped_column(BigInteger, nodeinfo_id_seq, server_default=nodeinfo_id_seq.next_value(), primary_key=True, init=False)

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["user_id"   , lambda packet: packet["decoded"]["user"]["id"]       ],
		["longName"  , lambda packet: packet["decoded"]["user"]["longName"] ],
		["shortName" , lambda packet: packet["decoded"]["user"]["shortName"]],
		["macaddr"   , lambda packet: packet["decoded"]["user"]["macaddr"]  ],
		["hwModel"   , lambda packet: packet["decoded"]["user"]["hwModel"]  ],
		["role"      , lambda packet: packet["decoded"]["user"]["role"]     ],
		["publicKey" , lambda packet: packet["decoded"]["user"]["publicKey"]],
	]

"""
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 2
  payload               : <class 'bytes'> b'\n'
  portnum               : <class 'str'> NODEINFO_APP
  user                  : <class 'dict'>
    hwModel             : <class 'str'> TRACKER_T1000_E
    id                  : <class 'str'> !8
    longName            : <class 'str'> A
    macaddr             : <class 'str'> 3F
    publicKey           : <class 'str'> IaC=
    role                : <class 'str'> TRACKER
    shortName           : <class 'str'> AAAA
  wantResponse          : <class 'bool'> True
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 32
rxRssi                  : <class 'int'> -16
rxSnr                   : <class 'float'> 13.0
rxTime                  : <class 'int'> 17
to                      : <class 'int'> 41
toId                    : <class 'str'> !f8
"""





position_id_seq = Sequence("Position_id_seq")

@reg.mapped_as_dataclass
class Position(Message):
	__tablename__ = "Position"

	latitudeI           : Mapped[int32] # 52
	longitudeI          : Mapped[int32] # 48
	altitude            : Mapped[int16] # 11
	time                : Mapped[int64] # 17
	PDOP                : Mapped[int16] # 272
	groundSpeed         : Mapped[int8 ] # 1
	groundTrack         : Mapped[int8 ] # 16
	satsInView          : Mapped[int8 ] # 6
	precisionBits       : Mapped[int8 ] # 32
	latitude            : Mapped[float] # 52
	longitude           : Mapped[float] #  4

	id                  : Mapped[int64] = mapped_column(BigInteger, position_id_seq, server_default=position_id_seq.next_value(), primary_key=True, init=False)

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["latitudeI"    , lambda packet: packet["decoded"]["position"]["latitudeI"]    ],
		["longitudeI"   , lambda packet: packet["decoded"]["position"]["longitudeI"]   ],
		["altitude"     , lambda packet: packet["decoded"]["position"]["altitude"]     ],
		["time"         , lambda packet: packet["decoded"]["position"]["time"]         ],
		["PDOP"         , lambda packet: packet["decoded"]["position"]["PDOP"]         ],
		["groundSpeed"  , lambda packet: packet["decoded"]["position"]["groundSpeed"]  ],
		["groundTrack"  , lambda packet: packet["decoded"]["position"]["groundTrack"]  ],
		["satsInView"   , lambda packet: packet["decoded"]["position"]["satsInView"]   ],
		["precisionBits", lambda packet: packet["decoded"]["position"]["precisionBits"]],
		["latitude"     , lambda packet: packet["decoded"]["position"]["latitude"]     ],
		["longitude"    , lambda packet: packet["decoded"]["position"]["longitude"]    ],
	]

"""
Received
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'\r\x81 '
  portnum               : <class 'str'> POSITION_APP
  position              : <class 'dict'>
    PDOP                : <class 'int'> 499
    altitude            : <class 'int'> -26
    groundSpeed         : <class 'int'> 0
    groundTrack         : <class 'int'>   290000000
    latitude            : <class 'float'> 52.0000000
    latitudeI           : <class 'int'>   520000000
    longitude           : <class 'float'> 4.0000000
    longitudeI          : <class 'int'>   48000000
    precisionBits       : <class 'int'> 32
    satsInView          : <class 'int'> 4
    time                : <class 'int'> 337
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 2500000000
rxRssi                  : <class 'int'> -11
rxSnr                   : <class 'float'> 15.25
rxTime                  : <class 'int'> 342
to                      : <class 'int'> 42
toId                    : <class 'str'> ^all
"""





textmessage_id_seq = Sequence("TextMessage_id_seq")

@reg.mapped_as_dataclass
class TextMessage(Message):
	__tablename__ = "TextMessage"

	payload     : Mapped[bytes]       # b'Hi'
	text        : Mapped[str  ]       # 'Hi'
	channel     : Mapped[int8 | None] # 1     - Public Broadcast
	wantAck     : Mapped[bool | None] # True, - Direct Message
	publicKey   : Mapped[str  | None] # 'zd9' - Direct Message
	pkiEncrypted: Mapped[bool | None] # True  - Direct Message

	id          : Mapped[int64] = mapped_column(BigInteger, textmessage_id_seq, server_default=textmessage_id_seq.next_value(), primary_key=True, init=False)

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["payload"     , lambda packet: packet["decoded"]["payload"]     ],
		["text"        , lambda packet: packet["decoded"]["text"]        ],

		["channel"     , lambda packet: packet.get("channel"     , None) ],
		["pkiEncrypted", lambda packet: packet.get("pkiEncrypted", None) ],
		["publicKey"   , lambda packet: packet.get("publicKey"   , None) ],
		["wantAck"     , lambda packet: packet.get("wantAck"     , None) ],
	]

"""
Received
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'Direct'
  portnum               : <class 'str'> TEXT_MESSAGE_APP
  text                  : <class 'str'> Direct
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 95
pkiEncrypted            : <class 'bool'> True
publicKey               : <class 'str'> Ia=
rxRssi                  : <class 'int'> -15
rxSnr                   : <class 'float'> 16.75
rxTime                  : <class 'int'> 47
to                      : <class 'int'> 41
toId                    : <class 'str'> !f8
wantAck                 : <class 'bool'> True

--------------------------------------------------

Received
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'PrivateB'
  portnum               : <class 'str'> TEXT_MESSAGE_APP
  text                  : <class 'str'> PrivateB
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 96
rxRssi                  : <class 'int'> -16
rxSnr                   : <class 'float'> 14.5
rxTime                  : <class 'int'> 98
to                      : <class 'int'> 42
toId                    : <class 'str'> ^all

--------------------------------------------------

Received
========
channel                 : <class 'int'> 1
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'PublicB'
  portnum               : <class 'str'> TEXT_MESSAGE_APP
  text                  : <class 'str'> PublicB
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 97
rxRssi                  : <class 'int'> -16
rxSnr                   : <class 'float'> 15.0
rxTime                  : <class 'int'> 929
to                      : <class 'int'> 42
toId                    : <class 'str'> ^all
"""





rangetest_id_seq = Sequence("RangeTest_id_seq")

@reg.mapped_as_dataclass
class RangeTest(Message):
	__tablename__ = "RangeTest"

	payload             : Mapped[bytes]     # b'Hi'
	text                : Mapped[str  ]     # 'Hi'

	id                  : Mapped[int64] = mapped_column(BigInteger, rangetest_id_seq, server_default=rangetest_id_seq.next_value(), primary_key=True, init=False)

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["payload"     , lambda packet: packet["decoded"]["payload"]     ],
		["text"        , lambda packet: packet["decoded"]["text"]        ],
	]

"""
Received
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'seq 2'
  portnum               : <class 'str'> RANGE_TEST_APP
  text                  : <class 'str'> seq 2
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
id                      : <class 'int'> 14
rxRssi                  : <class 'int'> -33
rxSnr                   : <class 'float'> 14.0
rxTime                  : <class 'int'> 17
to                      : <class 'int'> 42
toId                    : <class 'str'> ^all
"""



nodes_id_seq = Sequence("nodes_id_seq")

@reg.mapped_as_dataclass
class Nodes(Fields):
	__tablename__ = "Nodes"

	hopsAway            : Mapped[int8  | None]  # 0
	lastHeard           : Mapped[int64]         # 1700000000
	num                 : Mapped[int64]         # 24
	snr                 : Mapped[float]         # 16.0
	isFavorite          : Mapped[bool  | None]  # True

	airUtilTx           : Mapped[float]         # 3.1853054
	batteryLevel        : Mapped[int8 ]         # 64
	channelUtilization  : Mapped[float]         # 0.0
	uptimeSeconds       : Mapped[int64]         # 16792
	voltage             : Mapped[float]         # 3.836

	altitude            : Mapped[int16 | None]  # 18
	latitude            : Mapped[float | None]  # 52.0000000
	latitudeI           : Mapped[int32 | None]  #  520000000
	longitude           : Mapped[float | None]  #  4.0000000
	longitudeI          : Mapped[int32 | None]  #   48000000
	time                : Mapped[int64]         #  170000000

	hwModel             : Mapped[str]           # TRACKER_T1000_E
	user_id             : Mapped[str]           # !8fffffff
	longName            : Mapped[str]           # Aaaaaaa
	macaddr             : Mapped[str]           # 3Fffffff
	publicKey           : Mapped[str]           # Ia
	role                : Mapped[str]           # TRACKER
	shortName           : Mapped[str]           # AAAA

	id                  : Mapped[int64] = mapped_column(BigInteger, nodes_id_seq, server_default=nodes_id_seq.next_value(), primary_key=True, init=False)

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["hopsAway"          , lambda data: data.get("hopsAway", None) ],
		["lastHeard"         , lambda data: data["lastHeard"] ],
		["num"               , lambda data: data["num"] ],
		["snr"               , lambda data: data["snr"] ],
		["isFavorite"        , lambda data: data.get("isFavorite", None) ],

		["airUtilTx"         , lambda data: data["deviceMetrics"]["airUtilTx"]          ],
		["batteryLevel"      , lambda data: data["deviceMetrics"]["batteryLevel"]       ],
		["channelUtilization", lambda data: data["deviceMetrics"]["channelUtilization"] ],
		["uptimeSeconds"     , lambda data: data["deviceMetrics"]["uptimeSeconds"]      ],
		["voltage"           , lambda data: data["deviceMetrics"]["voltage"]            ],

		["altitude"          , lambda data: data["position"].get("altitude"  , None)],
		["latitude"          , lambda data: data["position"].get("latitude"  , None)],
		["latitudeI"         , lambda data: data["position"].get("latitudeI" , None)],
		["longitude"         , lambda data: data["position"].get("longitude" , None)],
		["longitudeI"        , lambda data: data["position"].get("longitudeI", None)],
		["time"              , lambda data: data["position"][    "time"]            ],

		["hwModel"           , lambda data: data["user"]["hwModel"]],
		["user_id"           , lambda data: data["user"]["id"]],
		["longName"          , lambda data: data["user"]["longName"]],
		["macaddr"           , lambda data: data["user"]["macaddr"]],
		["publicKey"         , lambda data: data["user"]["publicKey"]],
		["role"              , lambda data: data["user"]["role"]],
		["shortName"         , lambda data: data["user"]["shortName"]],
	]

	@classmethod
	def from_nodes(cls, nodes) -> "list[Node]":
		instances = [None] * len(nodes)
		for pos, (node_id, data) in enumerate(sorted(nodes.items())):
			#print("node_id", node_id)
			#print("data", data)
			inst = cls.from_packet(data)
			#print(inst)
			instances[pos] = inst
		return instances

"""
2406480062              : <class 'dict'>
  hopsAway              : <class 'int'> 0
  lastHeard             : <class 'int'> 1700000000
  num                   : <class 'int'> 2400000000
  snr                   : <class 'float'> 16.0

  deviceMetrics         : <class 'dict'>
    airUtilTx           : <class 'float'> 3.1853054
    batteryLevel        : <class 'int'> 64
    channelUtilization  : <class 'float'> 0.0
    uptimeSeconds       : <class 'int'> 16792
    voltage             : <class 'float'> 3.836
  position              : <class 'dict'>
    altitude            : <class 'int'> 18
    latitude            : <class 'float'> 52.0000000
    latitudeI           : <class 'int'>    520000000
    longitude           : <class 'float'>  4.0000000
    longitudeI          : <class 'int'>     48000000
    time                : <class 'int'>    170000000
  user                  : <class 'dict'>
    hwModel             : <class 'str'> TRACKER_T1000_E
    id                  : <class 'str'> !8fffffff
    longName            : <class 'str'> Aaaaaaa
    macaddr             : <class 'str'> 3Fffffff
    publicKey           : <class 'str'> Ia
    role                : <class 'str'> TRACKER
    shortName           : <class 'str'> AAAA

4100000000              : <class 'dict'>
  isFavorite            : <class 'bool'> True
  lastHeard             : <class 'int'> 1700000000
  num                   : <class 'int'> 4100000000
  snr                   : <class 'float'> 12.25
  deviceMetrics         : <class 'dict'>
    airUtilTx           : <class 'float'> 3.5829444
    batteryLevel        : <class 'int'> 101
    channelUtilization  : <class 'float'> 0.0
    uptimeSeconds       : <class 'int'> 38059
    voltage             : <class 'float'> 4.156
  position              : <class 'dict'>
    time                : <class 'int'> 1700000000
  user                  : <class 'dict'>
    hwModel             : <class 'str'> TRACKER_T1000_E
    id                  : <class 'str'> !f8ffffff
    longName            : <class 'str'> Sssss
    macaddr             : <class 'str'> /pfffff
    publicKey           : <class 'str'> zd9
    role                : <class 'str'> TRACKER
    shortName           : <class 'str'> SSSS
"""
