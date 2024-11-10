from ._base import *


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




# https://sqlmodel.tiangolo.com/tutorial/where/?h=select#where-and-expressions
def SelectSharedFilter(session: Session, cls: Message, filter_data: SharedFilterQuery):
	sel = select(cls).offset(filter_data.offset).limit(filter_data.limit)
	return sel

def SharedFilter(session: Session, cls: Message, filter_data: SharedFilterQuery):
	sel   = SelectSharedFilter(session=session, cls=cls, filter_data=filter_data)
	query = session.exec(sel)
	res   = [q.to_dataclass() for q in query.all()]
	return res

def TimedFilter(session: Session, cls: Message, filter_data: SharedFilterQuery):
	sel   = SelectSharedFilter(session=session, cls=cls, filter_data=filter_data)
	query = session.exec(sel)
	res   = [q.to_dataclass() for q in query.all()]
	return res


	# if todo_filter.key_contains is not None:
	# 	query = query.filter(TodoInDB.key.contains(todo_filter.key_contains))

	# if todo_filter.value_contains is not None:
	# 	query = query.filter(TodoInDB.value.contains(todo_filter.value_contains))

	# if todo_filter.done is not None:
	# 	query = query.filter(TodoInDB.done == todo_filter.done)

	# if todo_filter.limit is not None:
	# 	query = query.limit(todo_filter.limit)

	# return [Todo(key=todo.key, value=todo.value, done=todo.done) for todo in query]
	# return query
	# return [q.to_dataclass() for q in query.all()]

# https://donnypeeters.com/blog/fastapi-sqlalchemy/
# class BaseFilter:
#     def __init__(self, session: Session):
#         self._session: Session = session

#     def save(self, todo: Todo):
#         self._session.add(TodoInDB(key=todo.key, value=todo.value))

#     def get_by_key(self, key: str) -> Todo | None:
#         instance = self._session.query(TodoInDB).filter(TodoInDB.key == key).first()

#         if instance:
#             return Todo(key=instance.key, value=instance.value, done=instance.done)

#     def get(self, todo_filter: TodoFilter) -> List[Todo]:
#         query = self._session.query(TodoInDB)

#         if todo_filter.key_contains is not None:
#             query = query.filter(TodoInDB.key.contains(todo_filter.key_contains))

#         if todo_filter.value_contains is not None:
#             query = query.filter(TodoInDB.value.contains(todo_filter.value_contains))

#         if todo_filter.done is not None:
#             query = query.filter(TodoInDB.done == todo_filter.done)

#         if todo_filter.limit is not None:
#             query = query.limit(todo_filter.limit)

#         return [Todo(key=todo.key, value=todo.value, done=todo.done) for todo in query]
