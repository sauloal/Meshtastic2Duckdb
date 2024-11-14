from ._base    import *
from ._message import *


class TelemetryClass(MessageClass):
	__tablename__       = "telemetry"
	__ormclass__        = lambda: Telemetry

	time                : int64        # 1700000000
	batteryLevel        : int8  | None # 76
	voltage             : float | None # 3.956
	channelUtilization  : float | None # 5.8016667
	airUtilTx           : float | None # 4.323389
	uptimeSeconds       : int32 | None # 51470
	numPacketsTx        : int32 | None # 62
	numPacketsRx        : int32 | None # 103
	numOnlineNodes      : int16 | None # 3
	numTotalNodes       : int16 | None # 3
	lux                 : float | None # 0.0
	temperature         : float | None # 25.240046

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


telemetry_id_seq = gen_id_seq("telemetry")

class Telemetry(Message, SQLModel, table=True):
	__dataclass__ = lambda: TelemetryClass
	__filter__    = lambda: TelemetryFilterQuery

	time                : int64        = Field(              sa_type=BigInteger()  , nullable=False             ) # 17000000000
	batteryLevel        : int8  | None = Field(default=None, sa_type=SmallInteger(), nullable=True , index=True ) # 76
	voltage             : float | None = Field(default=None, sa_type=Float()       , nullable=True              ) # 3.956
	channelUtilization  : float | None = Field(default=None, sa_type=Float()       , nullable=True              ) # 5.8016667
	airUtilTx           : float | None = Field(default=None, sa_type=Float()       , nullable=True              ) # 4.323389
	uptimeSeconds       : int32 | None = Field(default=None, sa_type=Integer()     , nullable=True              ) # 51470
	numPacketsTx        : int32 | None = Field(default=None, sa_type=Integer()     , nullable=True              ) # 62
	numPacketsRx        : int32 | None = Field(default=None, sa_type=Integer()     , nullable=True              ) # 103
	numOnlineNodes      : int16 | None = Field(default=None, sa_type=SmallInteger(), nullable=True              ) # 3
	numTotalNodes       : int16 | None = Field(default=None, sa_type=SmallInteger(), nullable=True              ) # 3
	lux                 : float | None = Field(default=None, sa_type=Float()       , nullable=True , index=True ) # 0.0
	temperature         : float | None = Field(default=None, sa_type=Float()       , nullable=True , index=True ) # 25.240046

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": telemetry_id_seq.next_value()}, nullable=True)


"""
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
"""

class TelemetryFilterQueryParams(TimedFilterQueryParams):
	minBatteryLevel: Annotated[Optional[int  ], Query(default=None, ge=0  , le=100 ) ]
	hasLux         : Annotated[Optional[bool ], Query(default=None, ge=0           ) ]
	hasTemperature : Annotated[Optional[bool ], Query(default=None, ge=-50, le=100 ) ]

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		if self.minBatteryLevel is not None:
			print(" MIN BAT     ", self.minBatteryLevel)
			qry = qry.where(cls.batteryLevel is not None            )
			qry = qry.where(cls.batteryLevel >= self.minBatteryLevel)

		if self.hasLux is not None:
			print(" HAS LUX     ", self.hasLux)
			qry = qry.where(cls.lux is not None)

		if self.hasTemperature is not None:
			print(" HAS TEMPERATURE", self.hasTemperature)
			qry = qry.where(cls.temperature is not None)

		return qry

TelemetryFilterQuery = Annotated[TelemetryFilterQueryParams, Depends(TelemetryFilterQueryParams)]


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
