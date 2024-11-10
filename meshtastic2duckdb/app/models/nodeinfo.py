from ._base    import *
from ._message import *


class NodeInfoClass(MessageClass):
	__tablename__       = "nodeinfo"
	__ormclass__        = "NodeInfo"

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
	user_id             : str          = Field(nullable=False, sa_type=Text()) # !a
	longName            : str          = Field(nullable=False, sa_type=Text()) # M
	shortName           : str          = Field(nullable=False, sa_type=Text()) # M
	macaddr             : str          = Field(nullable=False, sa_type=Text()) # 8Z
	hwModel             : str          = Field(nullable=False, sa_type=Text()) # TRACKER_T1000_E
	role                : str          = Field(nullable=False, sa_type=Text()) # TRACKER
	publicKey           : str          = Field(nullable=False, sa_type=Text()) # S3

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

