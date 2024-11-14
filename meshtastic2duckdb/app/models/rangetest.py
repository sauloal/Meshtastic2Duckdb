from ._base    import *
from ._message import *

class RangeTestClass(MessageClass):
	__tablename__       = "rangetest"
	__ormclass__        = lambda: RangeTest

	payload             : bytes # b'Hi'
	text                : str   # 'Hi'

	_fields: typing.ClassVar[list[tuple[str, typing.Callable]]] = [
		["payload"     , lambda packet: packet["decoded"]["payload"]     ],
		["text"        , lambda packet: packet["decoded"]["text"]        ],
	]


rangetest_id_seq = gen_id_seq("rangetest")

class RangeTest(Message, SQLModel, table=True):
	__dataclass__ = lambda: RangeTestClass
	__filter__    = lambda: TimedFilterQuery

	payload             : bytes        = Field(nullable=False, sa_type=LargeBinary()) # b'Hi'
	text                : str          = Field(nullable=False, sa_type=Text()       ) # 'Hi'

	id                  : int64 | None = Field(primary_key=True, sa_column_kwargs={"server_default": rangetest_id_seq.next_value()}, nullable=True)

"""
Received
========
decoded                 : <class 'dict'>
  bitfield              : <class 'int'> 0
  payload               : <class 'bytes'> b'seq 2'
  portnum               : <class 'str'> RANGE_TEST_APP
  text                  : <class 'str'> seq 2
from                    : <class 'int'> 24
fromId                  : <class 'str'> !8f
id                      : <class 'int'> 14
rxRssi                  : <class 'int'> -33
rxSnr                   : <class 'float'> 14.0
rxTime                  : <class 'int'> 17
to                      : <class 'int'> 42
toId                    : <class 'str'> ^all
"""
