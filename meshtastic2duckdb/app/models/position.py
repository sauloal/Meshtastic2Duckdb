from ._base    import *
from ._message import *
from fastapi   import params as fastapi_params

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

	minLatitude   : Annotated[Optional[float], Query(default=None, ge=-90,         le=90         ) ]
	maxLatitude   : Annotated[Optional[float], Query(default=None, ge=-90,         le=90         ) ]

	minLongitude  : Annotated[Optional[float], Query(default=None, ge=-90,         le=90         ) ]
	maxLongitude  : Annotated[Optional[float], Query(default=None, ge=-90,         le=90         ) ]

	minAltitude   : Annotated[Optional[int  ], Query(default=None, ge=-50,         le=100        ) ]
	maxAltitude   : Annotated[Optional[int  ], Query(default=None, ge=-50,         le=100        ) ]

	minPDOP       : Annotated[Optional[int  ], Query(default=None, ge=0,           le=2048       ) ]
	maxPDOP       : Annotated[Optional[int  ], Query(default=None, ge=0,           le=2048       ) ]

	minGroundSpeed: Annotated[Optional[int  ], Query(default=None, ge=0,           le=256        ) ]
	maxGroundSpeed: Annotated[Optional[int  ], Query(default=None, ge=0,           le=256        ) ]

	@classmethod
	def endpoints(cls):
		return {
			**{
				"by-has-location": ("hasLocation"   , bool  , False),
			},
			**TimedFilterQueryParams.endpoints()
		}

	def _filter(self, qry, cls):
		#print(f"PositionFilterQueryParams {self} qry {qry} cls {cls}")

		for filterName, colName in [
				["LatitudeI"  , "latitudeI"  ],
				["LongitudeI" , "longitudeI" ],
				["Latitude"   , "latitude"   ],
				["Longitude"  , "longitude"  ],
				["Altitude"   , "altitude"   ],
				["PDOP"       , "PDOP"       ],
				["GroundSpeed", "GroundSpeed"],
			]:
			for func in ("min", "max"):
				selfAttr = getattr(self, func + filterName)
				if selfAttr is not None:
					clsAttr = getattr(cls, colName)
					print(" ", func, filterName, colName, selfAttr, clsAttr)
					if func == "min":
						qry = qry.where( clsAttr != None     )
						qry = qry.where( clsAttr >= selfAttr )
					else:
						qry = qry.where( clsAttr != None     )
						qry = qry.where( clsAttr <= selfAttr )

		if self.hasLocation is not None:
			self.hasLocation = str(self.hasLocation).lower() in "t,y,true,yes,1".split(",")

			#print(" HAS LOCATION", self.hasLocation)

			if self.hasLocation:
				qry = qry.where( cls.latitude != None )
			else:
				qry = qry.where( cls.latitude == None )

		return qry

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		qry = self._filter(qry, cls)

		return qry

PositionFilterQuery = Annotated[PositionFilterQueryParams, Depends(PositionFilterQueryParams)]

"""
@app.get( "/api/messages/position",                                summary = "Get Position Endpoints",       description = "Get Position Endpoints",    response_description = "Position Endpoints",    tags = ["Position"])
async def api_model_position_get():
	return { "endpoints": ["list", "by-has-location"] }

@app.post("/api/messages/position",                                summary = "Add Position Instance",        description = "Add Position Instances",    response_description = "None",                  tags = ["Position"],    status_code = status.HTTP_201_CREATED)
async def api_model_position_post(  data: models.PositionClass,    session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response ) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/position/list",                           summary = "Get Position Instances",       description = "Get Position Instances",    response_description = "List of Position",      tags = ["Position"])
async def api_model_position_list(                                 session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Position.__filter__() ) -> list[models.PositionClass]:
	return await api_model_get( model=models.Position,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/position/by-has-location/{has-location}", summary = "Get Position Instances",       description = "Get Position Instances",    response_description = "List of Position",      tags = ["Position"])
async def api_model_position_by_has_location(has_location: bool,   session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Position.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.hasLocation = has_location
	return await api_model_get( model=models.Position,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

"""

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

