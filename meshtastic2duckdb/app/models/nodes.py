from ._base    import *
from ._message import *


class NodesClass(ModelBaseClass):
	__tablename__       = "nodes"
	__ormclass__        = "Nodes"

	hopsAway            : int8  | None  # 0
	lastHeard           : int64 | None  # 1700000000
	num                 : int64         # 24
	snr                 : float         # 16.0
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
		["hopsAway"          , lambda data: data.get("hopsAway" , None) ],
		["lastHeard"         , lambda data: data.get("lastHeard", None) ],
		["num"               , lambda data: data["num"] ],
		["snr"               , lambda data: data["snr"] ],
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
class Nodes(SQLModel, table=True):
	hopsAway            : int8  | None  = Field( default=None, sa_type=SmallInteger(), nullable=True ) # 0
	lastHeard           : int64 | None  = Field( default=None, sa_type=BigInteger()  , nullable=True ) # 1700000000
	num                 : int64         = Field(               sa_type=BigInteger()  , nullable=False) # 24
	snr                 : float         = Field(               sa_type=Float()       , nullable=False) # 16.0
	isFavorite          : bool  | None  = Field( default=None, sa_type=Boolean()     , nullable=True ) # True

	airUtilTx           : float | None  = Field( default=None, sa_type=Float()       , nullable=True ) # 3.1853054
	batteryLevel        : int8  | None  = Field( default=None, sa_type=SmallInteger(), nullable=True ) # 64
	channelUtilization  : float | None  = Field( default=None, sa_type=Float()       , nullable=True ) # 0.0
	uptimeSeconds       : int64 | None  = Field( default=None, sa_type=BigInteger()  , nullable=True ) # 16792
	voltage             : float | None  = Field( default=None, sa_type=Float()       , nullable=True ) # 3.836

	altitude            : int16 | None  = Field( default=None, sa_type=SmallInteger(), nullable=True ) # 18
	latitude            : float | None  = Field( default=None, sa_type=Float()       , nullable=True ) # 52.0000000
	latitudeI           : int32 | None  = Field( default=None, sa_type=Integer()     , nullable=True ) #  520000000
	longitude           : float | None  = Field( default=None, sa_type=Float()       , nullable=True ) #  4.0000000
	longitudeI          : int32 | None  = Field( default=None, sa_type=Integer()     , nullable=True ) #   48000000
	time                : int64 | None  = Field( default=None, sa_type=BigInteger()  , nullable=True ) #  170000000

	hwModel             : str = Field(nullable=False, sa_type=Text() ) # TRACKER_T1000_E
	user_id             : str = Field(nullable=False, sa_type=Text() ) # !8fffffff
	longName            : str = Field(nullable=False, sa_type=Text() ) # Aaaaaaa
	macaddr             : str = Field(nullable=False, sa_type=Text() ) # 3Fffffff
	publicKey           : str = Field(nullable=False, sa_type=Text() ) # Ia
	role                : str = Field(nullable=False, sa_type=Text() ) # TRACKER
	shortName           : str = Field(nullable=False, sa_type=Text() ) # AAAA

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": nodes_id_seq.next_value()}, nullable=True)


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
