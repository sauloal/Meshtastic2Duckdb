from ._base    import *
from ._message import *

class TextMessageClass(MessageClass):
	__tablename__       = "textmessage"
	__ormclass__        = lambda: TextMessage

	payload             : bytes       # b'Hi'
	text                : str         # 'Hi'
	channel             : int8 | None # 1     - Public Broadcast
	wantAck             : bool | None # True, - Direct Message
	publicKey           : str  | None # 'zd9' - Direct Message
	pkiEncrypted        : bool | None # True  - Direct Message

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["payload"     , lambda packet: packet["decoded"]["payload"]     ],
		["text"        , lambda packet: packet["decoded"]["text"]        ],

		["channel"     , lambda packet: packet.get("channel"     , None) ],
		["pkiEncrypted", lambda packet: packet.get("pkiEncrypted", None) ],
		["publicKey"   , lambda packet: packet.get("publicKey"   , None) ],
		["wantAck"     , lambda packet: packet.get("wantAck"     , None) ],
	]



textmessage_id_seq = gen_id_seq("textmessage")

class TextMessage(Message, SQLModel, table=True):
	__dataclass__ = lambda: TextMessageClass
	__filter__    = lambda: TextMessageFilterQuery

	payload             : bytes        = Field(nullable=False, sa_type=LargeBinary()              ) # b'Hi'
	text                : str          = Field(nullable=False, sa_type=Text()                     ) # 'Hi'
	channel             : int8  | None = Field(nullable=True , sa_type=SmallInteger(), index=True ) # 1     - Public Broadcast
	wantAck             : bool  | None = Field(nullable=True , sa_type=Boolean()                  ) # True, - Direct Message
	publicKey           : str   | None = Field(nullable=True , sa_type=Text()                     ) # 'zd9' - Direct Message
	pkiEncrypted        : bool  | None = Field(nullable=True , sa_type=Boolean()     , index=True ) # True  - Direct Message

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": textmessage_id_seq.next_value()}, nullable=True)

class TextMessageFilterQueryParams(TimedFilterQueryParams):
	isPkiEncrypted: Annotated[Optional[bool ], Query(default=None ) ]
	channels      : Annotated[Optional[str  ], Query(default=None ) ]

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		if self.isPkiEncrypted is not None:
			print(" IS PKI ENCRYPTED", self.isPkiEncrypted)
			qry = qry.where(cls.pkiEncrypted == self.isPkiEncrypted)

		if self.channels is not None:
			print(" CHANNELS        ", self.channels)
			channels = self.channels.split(',')
			if channels:
				for b,c in enumerate(channels):
					try:
						channels[b] = int(c)
						assert channels[b] < 16
					except:
						raise HTTPException(status_code=400, detail="INVALID CHANNEL: " + ",".join(c for c in channels))

				qry = qry.where(cls.channel.in_( channels ))

		return qry

TextMessageFilterQuery = Annotated[TextMessageFilterQueryParams, Depends(TextMessageFilterQueryParams)]

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

