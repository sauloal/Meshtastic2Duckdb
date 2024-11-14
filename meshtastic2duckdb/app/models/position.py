from ._base    import *
from ._message import *


class PositionClass(MessageClass):
	__tablename__       = "position"
	__ormclass__        = lambda: Position

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
	__dataclass__ = lambda: PositionClass
	__filter__    = lambda: PositionFilterQuery

	latitudeI           : int32        = Field(              sa_type=Integer()       , nullable=False , index=True ) # 52
	longitudeI          : int32        = Field(              sa_type=Integer()       , nullable=False , index=True ) # 48

	latitude            : float        = Field(              sa_type=Float()         , nullable=False , index=True ) # 52
	longitude           : float        = Field(              sa_type=Float()         , nullable=False , index=True ) #  4

	altitude            : int16        = Field(              sa_type=SmallInteger()  , nullable=False , index=True ) # 11

	time                : int64        = Field(              sa_type=BigInteger()    , nullable=False              ) # 17
	PDOP                : int16        = Field(              sa_type=SmallInteger()  , nullable=False              ) # 272
	groundSpeed         : int8         = Field(              sa_type=SmallInteger()  , nullable=False , index=True ) # 1
	groundTrack         : int64        = Field(              sa_type=BigInteger()    , nullable=False , index=True ) # 16
	satsInView          : int8         = Field(              sa_type=SmallInteger()  , nullable=False              ) # 6
	precisionBits       : int8         = Field(              sa_type=SmallInteger()  , nullable=False              ) # 32

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": position_id_seq.next_value()}, nullable=True)


class PositionFilterQueryParams(TimedFilterQueryParams):
	hasLocation   : Annotated[Optional[bool ], Query(default=None ) ]

	minLatitudeI  : Annotated[Optional[int  ], Query(default=None, ge=-90_000_000, le=90_000_000 ) ]
	maxLatitudeI  : Annotated[Optional[int  ], Query(default=None, ge=-90_000_000, le=90_000_000 ) ]

	minLongitudeI : Annotated[Optional[int  ], Query(default=None, ge=-90_000_000, le=90_000_000 ) ]
	maxLongitudeI : Annotated[Optional[int  ], Query(default=None, ge=-90_000_000, le=90_000_000 ) ]

	minLatitude   : Annotated[Optional[float], Query(default=None, ge=-90, le=90 ) ]
	maxLatitude   : Annotated[Optional[float], Query(default=None, ge=-90, le=90 ) ]

	minLongitude  : Annotated[Optional[float], Query(default=None, ge=-90, le=90 ) ]
	maxLongitude  : Annotated[Optional[float], Query(default=None, ge=-90, le=90 ) ]

	minAltitude   : Annotated[Optional[int  ], Query(default=None, ge=-50, le=100 ) ]
	maxAltitude   : Annotated[Optional[int  ], Query(default=None, ge=-50, le=100 ) ]

	minPDOP       : Annotated[Optional[int  ], Query(default=None, ge=0, le=2048 ) ]
	maxPDOP       : Annotated[Optional[int  ], Query(default=None, ge=0, le=2048 ) ]

	minGroundSpeed: Annotated[Optional[int  ], Query(default=None, ge=0, le=256 ) ]
	maxGroundSpeed: Annotated[Optional[int  ], Query(default=None, ge=0, le=256) ]

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		for filterName, colName in [
				["LatitudeI"  , "latitudeI"  ],
				["LongitudeI" , "longitudeI" ],
				["Latitude"   , "latitude"   ],
				["Longitude"  , "longitude"  ],
				["Altitude"   , "altitude"   ],
				["PDOP"       , "PDOP"       ],
				["GroundSpeed", "groundSpeed"],
			]:
			for func in ("min", "max"):
				selfAttr = getattr(self, func + filterName)
				if selfAttr is not None:
					clsAttr = getattr(cls, colName)
					print(" ", func, filterName, colName, selfAttr, clsAttr)
					if func == "min":
						qry = qry.where(clsAttr is not None)
						qry = qry.where(clsAttr >= selfAttr)
					else:
						qry = qry.where(clsAttr is not None)
						qry = qry.where(clsAttr <= selfAttr)

		if self.hasLocation is not None:
			print(" HAS LOCATION", self.hasLocation)
			qry = qry.where(cls.latitude is not None)

		return qry

PositionFilterQuery = Annotated[PositionFilterQueryParams, Depends(PositionFilterQueryParams)]


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

