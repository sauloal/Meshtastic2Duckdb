from ._base import *
from . import _converters as converters

class MessageClass(ModelBaseClass):
	from_node : int64
	to_node   : int64

	fromId    : str   | None
	toId      : str   | None

	rxTime    : int64 | None
	rxRssi    : int16 | None
	rxSnr     : float | None

	hopStart  : int8  | None
	hopLimit  : int8  | None

	message_id: int64
	priority  : str   | None

	portnum   : str
	bitfield  : int8  | None

	_fields       : typing.ClassVar[list[tuple[str, typing.Callable]]] = []
	_shared_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["from_node"  , lambda packet: packet["from"]                         ],
		["to_node"    , lambda packet: packet["to"]                           ],

		["fromId"     , lambda packet: packet.get("fromId"  , None)           ],
		["toId"       , lambda packet: packet.get("toId"    , None)           ],

		["rxTime"     , lambda packet: packet.get("rxTime"  , None)           ],
		["rxRssi"     , lambda packet: packet.get("rxRssi"  , None)           ],
		["rxSnr"      , lambda packet: packet.get("rxSnr"   , None)           ],

		["hopStart"   , lambda packet: packet.get("hopStart", None)           ],
		["hopLimit"   , lambda packet: packet.get("hopLimit", None)           ],

		["message_id" , lambda packet: packet["id"]                           ],
		["priority"   , lambda packet: packet.get("priority", None)           ],

		["portnum"    , lambda packet: packet["decoded"]["portnum"]           ],
		["bitfield"   , lambda packet: packet["decoded"].get("bitfield", None)],
	]

	__pretty_names__ = {
		**ModelBaseClass.__pretty_names__,
		**{
			#"gateway_receive_time": (0,"Gateway Receive Time", converters.epoch_to_str)
			"from_node" : (1, "From Node" , converters.echo),
			"to_node"   : (1, "To Node"   , converters.echo),

			"fromId"    : (2, "From ID"   , converters.user_id),
			"toId"      : (2, "To ID"     , converters.user_id),

			"rxTime"    : (3, "Rx Time"   , converters.epoch_to_str),
			"rxRssi"    : (3, "Rx Rssi"   , converters.echo),
			"rxSnr"     : (3, "Rx Snr"    , converters.echo),

			"hopStart"  : (6, "Hop Start" , converters.echo),
			"hopLimit"  : (6, "Hop Limit" , converters.echo),

			"message_id": (5, "Message ID", converters.echo),
			"priority"  : (5, "Priority"  , converters.echo),

			"portnum"   : (6, "Port Num"  , converters.echo),
			"bitfield"  : (6, "Bit Field" , converters.echo),
		}
	}




class Message(ModelBase, SQLModel):
	from_node : int64        = Field(              sa_type=BigInteger()  , nullable=False )
	to_node   : int64        = Field(              sa_type=BigInteger()  , nullable=False )

	fromId    : str   | None = Field(              sa_type=Text()        , nullable=True  )
	toId      : str          = Field(              sa_type=Text()        , nullable=False )

	rxTime    : int64 | None = Field(default=None, sa_type=BigInteger()  , nullable=True  )
	rxRssi    : int16 | None = Field(default=None, sa_type=SmallInteger(), nullable=True  )
	rxSnr     : float | None = Field(default=None, sa_type=Float()       , nullable=True  )

	hopStart  : int8  | None = Field(default=None, sa_type=SmallInteger(), nullable=True  )
	hopLimit  : int8  | None = Field(default=None, sa_type=SmallInteger(), nullable=True  )

	message_id: int64        = Field(              sa_type=BigInteger()  , nullable=False )
	priority  : str   | None = Field(              sa_type=Text()        , nullable=True  )

	portnum   : str          = Field(              sa_type=Text()        , nullable=False )
	bitfield  : int8  | None = Field(default=None, sa_type=SmallInteger(), nullable=True  )

	__dataclass__ = None
	__filter__    = None

	@classmethod
	def get_data_class(cls):
		return cls.__dataclass__()

	@classmethod
	def get_filter_class(cls):
		return cls.__filter__()
