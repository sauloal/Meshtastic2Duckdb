from datetime import datetime, timedelta

from typing import Annotated, Optional, Generator, Literal

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlmodel import select

from .. import dbgenerics





def get_now() -> int:
	return int(datetime.timestamp(datetime.now()))

def get_since() -> int:
	return int(datetime.timestamp(datetime.now() - timedelta(days=1)))

# https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#classes-as-dependencies_1
class SharedFilterQueryParams(BaseModel):
	offset  : Annotated[ int                                , Query(default=0  , ge=0)         ]
	limit   : Annotated[ int                                , Query(default=10 , gt=0, le=100) ]
	dryrun  : Annotated[ bool                               , Query(default=False)             ]
	order   : Annotated[ Literal["asc"       , "dsc"       ], Query(default="asc")             ]
	# reversed: Annotated[ bool                               , Query(default=False)             ]
	# order_by: Annotated[ Literal["created_at", "updated_at"], Query(default="created_at")      ]
	# group_by: Annotated[ Literal["created_at", "updated_at"], Query(default="created_at")      ]
	# tags    : list[str] = []
	q       : Annotated[ str | None                         , Query(default=None)              ]

	# https://sqlmodel.tiangolo.com/tutorial/where/?h=select#where-and-expressions
	def __call__(self, session: dbgenerics.GenericSession, cls):
		sel = select(cls)
		qry = sel.offset(self.offset).limit(self.limit)
		return qry

	@classmethod
	def endpoints(cls):
		return {}

SharedFilterQuery = Annotated[SharedFilterQueryParams, Depends(SharedFilterQueryParams)]





class TimedFilterQueryParams(SharedFilterQueryParams):
	since   : Annotated[Optional[int]  , Query(default=Depends(get_since), ge=0)       ]
	until   : Annotated[Optional[int]  , Query(default=None              , ge=0)       ]

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = SharedFilterQueryParams.__call__(self, session, cls)

		if self.since is not None:
			print(" SINCE", self.since)
			qry = qry.where(cls.gateway_receive_time >= self.since)

		if self.until is not None:
			print(" UNTIL", self.until)
			qry = qry.where(cls.gateway_receive_time <= self.until)

		return qry

	@classmethod
	def endpoints(cls):
		return {
			**{
				"since": ("since", int  , False),
				"until": ("until", int  , False),
			},
			**SharedFilterQueryParams.endpoints()
		}

TimedFilterQuery = Annotated[TimedFilterQueryParams, Depends(TimedFilterQueryParams)]



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
