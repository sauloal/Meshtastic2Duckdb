from ._base    import *
from ._message import *


class NodeInfoClass(MessageClass):
	__tablename__       = "nodeinfo"
	__ormclass__        = lambda: NodeInfo

	user_id             : str # !a
	longName            : str # M
	shortName           : str # M
	macaddr             : str # 8Z
	hwModel             : str # TRACKER_T1000_E
	role                : str # TRACKER
	publicKey           : str # S3

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["user_id"   , lambda packet: packet["decoded"]["user"]["id"]       ],
		["longName"  , lambda packet: packet["decoded"]["user"]["longName"] ],
		["shortName" , lambda packet: packet["decoded"]["user"]["shortName"]],
		["macaddr"   , lambda packet: packet["decoded"]["user"]["macaddr"]  ],
		["hwModel"   , lambda packet: packet["decoded"]["user"]["hwModel"]  ],
		["role"      , lambda packet: packet["decoded"]["user"]["role"]     ],
		["publicKey" , lambda packet: packet["decoded"]["user"]["publicKey"]],
	]

nodeinfo_id_seq = gen_id_seq("nodeinfo")
class NodeInfo(Message, SQLModel, table=True):
	__dataclass__ = lambda: NodeInfoClass
	__filter__    = lambda: NodeInfoFilterQuery

	user_id             : str          = Field(nullable=False, sa_type=Text(), index=True) # !a
	longName            : str          = Field(nullable=False, sa_type=Text(), index=True) # M
	shortName           : str          = Field(nullable=False, sa_type=Text(), index=True) # M
	macaddr             : str          = Field(nullable=False, sa_type=Text()            ) # 8Z
	hwModel             : str          = Field(nullable=False, sa_type=Text(), index=True) # TRACKER_T1000_E
	role                : str          = Field(nullable=False, sa_type=Text(), index=True) # TRACKER
	publicKey           : str          = Field(nullable=False, sa_type=Text()            ) # S3

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": nodeinfo_id_seq.next_value()}, nullable=True)

"""
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 2
  payload               : <class 'bytes'> b'\n'
  portnum               : <class 'str'> NODEINFO_APP
  user                  : <class 'dict'>
    hwModel             : <class 'str'> TRACKER_T1000_E
    id                  : <class 'str'> !8
    longName            : <class 'str'> A
    macaddr             : <class 'str'> 3F
    publicKey           : <class 'str'> IaC=
    role                : <class 'str'> TRACKER
    shortName           : <class 'str'> AAAA
  wantResponse          : <class 'bool'> True
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
hopLimit                : <class 'int'> 3
hopStart                : <class 'int'> 3
id                      : <class 'int'> 32
rxRssi                  : <class 'int'> -16
rxSnr                   : <class 'float'> 13.0
rxTime                  : <class 'int'> 17
to                      : <class 'int'> 41
toId                    : <class 'str'> !f8
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


class NodeInfoFilterQueryParams(TimedFilterQueryParams):
	userIds    : Annotated[Optional[str  ], Query(default=None ) ]
	shortNames : Annotated[Optional[str  ], Query(default=None ) ]
	longNames  : Annotated[Optional[str  ], Query(default=None ) ]
	hwModels   : Annotated[Optional[str  ], Query(default=None ) ]
	roles      : Annotated[Optional[str  ], Query(default=None ) ]

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

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

		if self.hwModels is not None:
			print(" HW MODELS   ", self.hwModels)
			hw_models = self.hwModels.split(',')
			if long_names:
				qry = qry.where(cls.hwModel.in_( hw_models ))

		if self.roles is not None:
			roles = self.roles.split(",")
			if roles:
				print(" ROLES       ", self.roles)
				roles = self.roles.split(",")
				if not all(r in Roles.__members__ for r in roles):
					raise HTTPException(status_code=400, detail="INVALID ROLES: " + ",".join(r for r in roles if r not in Roles.__members__))
				qry = qry.where( cls.role.in_(roles) )

		return qry

NodeInfoFilterQuery = Annotated[NodeInfoFilterQueryParams, Depends(NodeInfoFilterQueryParams)]
