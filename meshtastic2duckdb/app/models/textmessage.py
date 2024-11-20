from ._base    import *
from ._message import *
from fastapi   import params as fastapi_params

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

	@classmethod
	def endpoints(cls):
		return {
			**{
				"by-is-encrypted": ("isPkiEncrypted", bool , False ),
				"by-channel"     : ("channels"      , int  , True  ),
			},
			**TimedFilterQueryParams.endpoints()
		}

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		if self.isPkiEncrypted is not None:
			self.isPkiEncrypted = str(self.isPkiEncrypted).lower()         in "t,y,true,yes,1".split(",")
			print(" IS PKI ENCRYPTED", self.isPkiEncrypted)
			qry = qry.where(cls.pkiEncrypted == self.isPkiEncrypted)

		if self.channels is not None:
			channels = self.channels
			if isinstance(channels, str):
				channels = channels.split(',')

			print(" CHANNELS        ", channels)

			if channels:
				for b,c in enumerate(channels):
					try:
						channels[b] = int(c)
						assert channels[b] < 16
					except:
						raise HTTPException(status_code=400, detail="INVALID CHANNEL: " + ",".join(str(c) for c in channels))

				print(" CHANNELS        ", channels)
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

"""
@app.get( "/api/messages/textmessage",                              summary = "Get TextMessage Endpoints",   description = "Get TextMessage Endpoints", response_description = "TextMessage Endpoints", tags = ["TextMessage"])
async def api_model_textmessage_get():
	return { "endpoints": ["list"] }

@app.post("/api/messages/textmessage",                              summary = "Add TextMessage Instance" ,   description = "Add TextMessage Instances", response_description = "None"                 , tags = ["TextMessage"], status_code = status.HTTP_201_CREATED)
async def api_model_textmessage_post(data: models.TextMessageClass, session_manager: db.SessionManagerDepRW, request: Request,                          response: Response ) -> None:
	return await api_model_post( data=data,                     session_manager=session_manager,         request=request,                           response=response )

@app.get( "/api/messages/textmessage/list",                         summary = "Get TextMessage Instances",   description = "Get TextMessage Instances", response_description = "List of TextMessage"  , tags = ["TextMessage"])
async def api_model_textmessage_list(                               session_manager: db.SessionManagerDepRO, request: Request,                          response: Response,     query_filter: models.TextMessage.__filter__() ) -> list[models.TextMessageClass]:
	return await api_model_get( model=models.TextMessage,       session_manager=session_manager,         request=request,                           response=response,      query_filter=query_filter  )
"""
