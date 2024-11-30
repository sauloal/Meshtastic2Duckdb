from ._base  import *
from .       import _converters as converters
from fastapi import params      as fastapi_params

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
			"from_node" : (50, "From Node" , converters.echo),
			"to_node"   : (50, "To Node"   , converters.echo),

			"fromId"    : (51, "From ID"   , converters.user_id),
			"toId"      : (51, "To ID"     , converters.user_id),

			"rxTime"    : (52, "Rx Time"   , converters.epoch_to_str),
			"rxRssi"    : (52, "Rx Rssi"   , converters.echo),
			"rxSnr"     : (52, "Rx Snr"    , converters.echo),

			"hopStart"  : (54, "Hop Start" , converters.echo),
			"hopLimit"  : (54, "Hop Limit" , converters.echo),

			"message_id": (53, "Message ID", converters.echo),
			"priority"  : (53, "Priority"  , converters.echo),

			"portnum"   : (54, "Port Num"  , converters.echo),
			"bitfield"  : (54, "Bit Field" , converters.echo),
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
	__filter__    = lambda: MessageFilterQuery

	@classmethod
	def get_data_class(cls):
		return cls.__dataclass__()

	@classmethod
	def get_filter_class(cls):
		return cls.__filter__()


class MessageFilterQueryParams(TimedFilterQueryParams):
	"""
        from_node : int64
        to_node   : int64

        fromId    : str   | None
        toId      : str   | None
	"""
	pass

	def __call__(self, session: dbgenerics.GenericSession, cls, filter_is_unique: str|None=None):
		qry = TimedFilterQueryParams.__call__(self, session, cls, filter_is_unique=filter_is_unique)

		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		#for a in ["since", "until", "time_from", "time_length"]:
		#	setattr(self, a, None if getattr(self, a) in ("",None) else getattr(self, a))

		return qry

	def gen_html_filters(self, url, query):
		#print("gen_html_filters :: SELF", self)

		from_nodes   = query("from_node")
		to_nodes     = query("to_node")
		from_ids     = query("fromId")
		to_ids       = query("toId")

		filter_opts = [
			[self, "from_nodes", "From Node", "select", [["-", ""]] + [[r,r] for r in from_nodes ]],
			[self, "to_nodes",   "To Node",   "select", [["-", ""]] + [[r,r] for r in to_nodes   ]],
			[self, "from_ids",   "From ID",   "select", [["-", ""]] + [[r,r] for r in from_ids   ]],
			[self, "to_ids",     "To ID",     "select", [["-", ""]] + [[r,r] for r in to_ids     ]],
		]

		filters     = TimedFilterQueryParams.gen_html_filters(self, url, query)
		filters.extend( filter_opts )

		return filters

	@classmethod
	def endpoints(cls):
		return {
			**{
				"from_nodes" : ("from_nodes" , int  , True ),
				"to_nodes"   : ("to_nodes"   , int  , True ),
				"from_ids"   : ("from_ids"   , int  , True ),
				"to_ids"     : ("to_ids"     , int  , True ),
			},
			**TimedFilterQueryParams.endpoints()
		}

MessageFilterQuery = Annotated[MessageFilterQueryParams, Depends(MessageFilterQueryParams)]



