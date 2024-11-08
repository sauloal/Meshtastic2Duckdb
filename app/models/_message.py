from ._base import *


class MessageClass(ModelBaseClass):
	from_node : int64
	to_node   : int64

	fromId    : str
	toId      : str

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

		["fromId"     , lambda packet: packet["fromId"]                       ],
		["toId"       , lambda packet: packet["toId"]                         ],

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




class Message(SQLModel):
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

	@classmethod
	def from_dataclass(cls, inst: ModelBaseClass) -> "Message":
		return cls(**inst.toJSON())

	def to_dataclass(self, cls: ModelBaseClass) -> ModelBaseClass:
		return cls(**self.model_dump())
