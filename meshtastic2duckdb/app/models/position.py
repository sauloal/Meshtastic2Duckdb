from ._base    import *
from ._message import *


class PositionClass(MessageClass):
	__tablename__       = "position"
	__ormclass__        = "Position"

	latitudeI           : int32
	longitudeI          : int32
	altitude            : int16
	time                : int64
	PDOP                : int16
	groundSpeed         : int8
	groundTrack         : int64
	satsInView          : int8
	precisionBits       : int8
	latitude            : float
	longitude           : float

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


position_id_seq = gen_id_seq("position")

class Position(Message, SQLModel, table=True):
	latitudeI           : int32        = Field(              sa_type=Integer()       , nullable=False ) # 52
	longitudeI          : int32        = Field(              sa_type=Integer()       , nullable=False ) # 48
	altitude            : int16        = Field(              sa_type=SmallInteger()  , nullable=False ) # 11
	time                : int64        = Field(              sa_type=BigInteger()    , nullable=False ) # 17
	PDOP                : int16        = Field(              sa_type=SmallInteger()  , nullable=False ) # 272
	groundSpeed         : int8         = Field(              sa_type=SmallInteger()  , nullable=False ) # 1
	groundTrack         : int64        = Field(              sa_type=BigInteger()    , nullable=False ) # 16
	satsInView          : int8         = Field(              sa_type=SmallInteger()  , nullable=False ) # 6
	precisionBits       : int8         = Field(              sa_type=SmallInteger()  , nullable=False ) # 32
	latitude            : float        = Field(              sa_type=Float()         , nullable=False )# 52
	longitude           : float        = Field(              sa_type=Float()         , nullable=False ) #  4

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": position_id_seq.next_value()}, nullable=True)


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

