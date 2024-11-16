from ._base    import *
from ._message import *


class NodesClass(ModelBaseClass):
	__tablename__       = "nodes"
	__ormclass__        = lambda: Nodes

	hopsAway            : int8  | None  # 0
	lastHeard           : int64 | None  # 1700000000
	num                 : int64         # 24
	snr                 : float | None  # 16.0
	isFavorite          : bool  | None  # True

	airUtilTx           : float | None  # 3.1853054
	batteryLevel        : int8  | None  # 64
	channelUtilization  : float | None  # 0.0
	uptimeSeconds       : int64 | None  # 16792
	voltage             : float | None  # 3.836

	altitude            : int16 | None  # 18
	latitude            : float | None  # 52.0000000
	latitudeI           : int32 | None  #  520000000
	longitude           : float | None  #  4.0000000
	longitudeI          : int32 | None  #   48000000
	time                : int64 | None  #  170000000

	hwModel             : str           # TRACKER_T1000_E
	user_id             : str           # !8fffffff
	longName            : str           # Aaaaaaa
	macaddr             : str           # 3Fffffff
	publicKey           : str           # Ia
	role                : str           # TRACKER
	shortName           : str           # AAAA

	_shared_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = []
	_fields       : typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["hopsAway"          , lambda data: data.get("hopsAway"  , None) ],
		["lastHeard"         , lambda data: data.get("lastHeard" , None) ],
		["num"               , lambda data: data["num"] ],
		["snr"               , lambda data: data.get("snr"       , None) ],
		["isFavorite"        , lambda data: data.get("isFavorite", None) ],

		["airUtilTx"         , lambda data: data.get("deviceMetrics", {}).get("airUtilTx"         , None)],
		["batteryLevel"      , lambda data: data.get("deviceMetrics", {}).get("batteryLevel"      , None)],
		["channelUtilization", lambda data: data.get("deviceMetrics", {}).get("channelUtilization", None)],
		["uptimeSeconds"     , lambda data: data.get("deviceMetrics", {}).get("uptimeSeconds"     , None)],
		["voltage"           , lambda data: data.get("deviceMetrics", {}).get("voltage"           , None)],

		["altitude"          , lambda data: data.get("position", {}).get("altitude"  , None)],
		["latitude"          , lambda data: data.get("position", {}).get("latitude"  , None)],
		["latitudeI"         , lambda data: data.get("position", {}).get("latitudeI" , None)],
		["longitude"         , lambda data: data.get("position", {}).get("longitude" , None)],
		["longitudeI"        , lambda data: data.get("position", {}).get("longitudeI", None)],
		["time"              , lambda data: data.get("position", {}).get("time"      , None)],

		["hwModel"           , lambda data: data["user"]["hwModel"]],
		["user_id"           , lambda data: data["user"]["id"]],
		["longName"          , lambda data: data["user"]["longName"]],
		["macaddr"           , lambda data: data["user"]["macaddr"]],
		["publicKey"         , lambda data: data["user"]["publicKey"]],
		["role"              , lambda data: data["user"]["role"]],
		["shortName"         , lambda data: data["user"]["shortName"]],
	]



nodes_id_seq = gen_id_seq("nodes")
class Nodes(ModelBase, SQLModel, table=True):
	__dataclass__ = lambda: NodesClass
	__filter__    = lambda: NodesFilterQuery

	hopsAway            : int8  | None  = Field( default=None, sa_type=SmallInteger(), nullable=True              ) # 0
	lastHeard           : int64 | None  = Field( default=None, sa_type=BigInteger()  , nullable=True              ) # 1700000000
	num                 : int64         = Field(               sa_type=BigInteger()  , nullable=False             ) # 24
	snr                 : float | None  = Field( default=None, sa_type=Float()       , nullable=True              ) # 16.0
	isFavorite          : bool  | None  = Field( default=None, sa_type=Boolean()     , nullable=True , index=True ) # True

	airUtilTx           : float | None  = Field( default=None, sa_type=Float()       , nullable=True              ) # 3.1853054
	batteryLevel        : int8  | None  = Field( default=None, sa_type=SmallInteger(), nullable=True , index=True ) # 64
	channelUtilization  : float | None  = Field( default=None, sa_type=Float()       , nullable=True              ) # 0.0
	uptimeSeconds       : int64 | None  = Field( default=None, sa_type=BigInteger()  , nullable=True              ) # 16792
	voltage             : float | None  = Field( default=None, sa_type=Float()       , nullable=True              ) # 3.836

	altitude            : int16 | None  = Field( default=None, sa_type=SmallInteger(), nullable=True              ) # 18
	latitude            : float | None  = Field( default=None, sa_type=Float()       , nullable=True , index=True ) # 52.0000000
	latitudeI           : int32 | None  = Field( default=None, sa_type=Integer()     , nullable=True , index=True ) #  520000000
	longitude           : float | None  = Field( default=None, sa_type=Float()       , nullable=True , index=True ) #  4.0000000
	longitudeI          : int32 | None  = Field( default=None, sa_type=Integer()     , nullable=True , index=True ) #   48000000
	time                : int64 | None  = Field( default=None, sa_type=BigInteger()  , nullable=True , index=True ) #  170000000

	hwModel             : str           = Field(               sa_type=Text()        , nullable=False, index=True ) # TRACKER_T1000_E
	user_id             : str           = Field(               sa_type=Text()        , nullable=False, index=True ) # !8fffffff
	longName            : str           = Field(               sa_type=Text()        , nullable=False, index=True ) # Aaaaaaa
	macaddr             : str           = Field(               sa_type=Text()        , nullable=False             ) # 3Fffffff
	publicKey           : str           = Field(               sa_type=Text()        , nullable=False             ) # Ia
	role                : str           = Field(               sa_type=Text()        , nullable=False, index=True ) # TRACKER
	shortName           : str           = Field(               sa_type=Text()        , nullable=False, index=True ) # AAAA

	id                  : int64 | None  = Field(primary_key=True, sa_column_kwargs={"server_default": nodes_id_seq.next_value()}, nullable=True)


from enum import Enum
class Roles(str, Enum):
	#https://meshtastic.org/docs/configuration/radio/device/
	CLIENT         : str = "CLIENT"
	CLIENT_MUTE    : str = "CLIENT_MUTE"
	CLIENT_HIDDEN  : str = "CLIENT_HIDDEN"
	TRACKER        : str = "TRACKER"
	LOST_AND_FOUND : str = "LOST_AND_FOUND"
	SENSOR         : str = "SENSOR"
	TAK            : str = "TAK"
	TAK_TRACKER    : str = "TAK_TRACKER"
	REPEATER       : str = "REPEATER"
	ROUTER         : str = "ROUTER"





class NodesPositionFilterQueryParams(TimedFilterQueryParams):
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

	@classmethod
	def endpoints(cls):
		return {
			**{
				"by-has-location": ("hasLocation"   , bool  , False),
			},
			**TimedFilterQueryParams.endpoints()
		}

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)
		qry = self._filter(qry, cls)
		return qry

	def _filter(self, qry, cls):
		for filterName, colName in [
				["LatitudeI"  , "latitudeI"  ],
				["LongitudeI" , "longitudeI" ],
				["Latitude"   , "latitude"   ],
				["Longitude"  , "longitude"  ],
				["Altitude"   , "altitude"   ],
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

NodesPositionFilterQuery = Annotated[NodesPositionFilterQueryParams, Depends(NodesPositionFilterQueryParams)]






class NodesFilterQueryParams(NodesPositionFilterQueryParams):
	isFavorite    : Annotated[Optional[bool ], Query(default=None ) ]
	userIds       : Annotated[Optional[str  ], Query(default=None ) ]
	shortNames    : Annotated[Optional[str  ], Query(default=None ) ]
	longNames     : Annotated[Optional[str  ], Query(default=None ) ]
	roles         : Annotated[Optional[str  ], Query(default=None ) ]

	@classmethod
	def endpoints(cls):
		return {
			**{
				"by-is-favorite": ("isFavorite", bool , False),
				"by-user-id"    : ("userIds"   , str  , True ),
				"by-short-name" : ("shortNames", str  , True ),
				"by-long-name"  : ("longNames" , str  , True ),
				"by-role"       : ("roles"     , Roles, True ),
			},
			**NodesPositionFilterQueryParams.endpoints()
		}

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		if self.isFavorite is not None:
			print(" IS FAVORITE", self.isFavorite)
			qry = qry.where(cls.isFavorite == self.isFavorite)

		if self.userIds is not None:
			print(" USER IDS    ", self.userIds)
			user_ids = self.userIds.split(',')
			if user_ids:
				qry = qry.where(cls.user_id.in_( user_ids ))

		if self.shortNames is not None:
			print(" SHORT NAMES ", self.shortNames)
			short_names = self.shortNames.split(',')
			if short_names:
				qry = qry.where(cls.shortName.in_( short_names ))

		if self.longNames is not None:
			print(" LONG NAMES  ", self.longNames)
			long_names = self.longNames.split(',')
			if long_names:
				qry = qry.where(cls.longName.in_( long_names ))

		if self.roles is not None:
			roles = self.roles.split(",")
			if roles:
				print(" ROLES       ", self.roles)
				roles = self.roles.split(",")
				if not all(r in Roles.__members__ for r in roles):
					raise HTTPException(status_code=400, detail="INVALID ROLES: " + ",".join(r for r in roles if r not in Roles.__members__))
				qry = qry.where( cls.role.in_(roles) )

		qry = NodesPositionFilterQueryParams._filter(self, qry, cls)

		return qry

NodesFilterQuery = Annotated[NodesFilterQueryParams, Depends(NodesFilterQueryParams)]

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

"""
@app.get( "/api/messages/nodes",                                   summary = "Get Nodes Endpoints",          description = "Get Nodes Endpoints",       response_description = "Nodes Endpoints",       tags = ["Nodes"])
async def api_model_nodes_get():
	return { "endpoints": ["list", "by-is-favorite", "by-user-id", "by-short-name", "by-long-name", "by-role", "by-has-location"] }

@app.post("/api/messages/nodes",                                   summary = "Add Nodes Instances",          description = "Add Nodes Instances",       response_description = "None",                  tags = ["Nodes"],       status_code = status.HTTP_201_CREATED)
async def api_model_nodes_post(     data: models.NodesClass,       session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response) -> None:
	return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/nodes/list",                              summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_list(                                    session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodesClass]:
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-user-id/{user_id}",              summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_user_id(user_id: str,                 session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.userIds = [user_id]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-long-name/{long_name}",          summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_long_name(long_name: str,             session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.longNames = [long_name]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-short-name/{short_name}",        summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_short_name(short_name: str,           session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.shortNames = [short_name]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-role/{role}",                    summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_role(role: str,                       session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.roles = [role]
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-is-favorite/{favorite}",         summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_is_favorite(favorite: bool,           session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.isFavorite = favorite
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodes/by-has-location/{has-location}",    summary = "Get Nodes Instances",          description = "Get Nodes Instances",       response_description = "List of Nodes",         tags = ["Nodes"])
async def api_model_nodes_by_has_location(has_location: bool,      session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.Nodes.__filter__() ) -> list[models.NodeInfoClass]:
	query_filter.hasLocation = has_location
	return await api_model_get( model=models.Nodes,            session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )
"""
