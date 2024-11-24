from datetime import datetime, timedelta

from typing import Annotated, Optional, Generator, Literal

from fastapi  import Depends, Query, params as fastapi_params
from pydantic import BaseModel
from sqlmodel import select
from pydantic.functional_validators import AfterValidator

from .. import dbgenerics




delta_short_to_long = {
	"m": (lambda x: x     , "minutes"),
	"h": (lambda x: x     , "hours"  ),
	"D": (lambda x: x     , "days"   ),
	"W": (lambda x: x     , "weeks"  ),
	"M": (lambda x: x *  4, "weeks"  ),
	"Y": (lambda x: x * 52, "weeks"  )
}

def get_now() -> int:
	return int(datetime.timestamp(datetime.now()))

def get_since() -> int:
	return int(datetime.timestamp(datetime.now() - timedelta(days=1)))

def get_timestamp(value:int, unit:str, begin=None, after=False, verbose=False):
	if verbose: print(f"{value=} {unit=} {begin=} {after=}")

	if begin is None:
		begin = get_now()

	delta_func, delta_key  = delta_short_to_long[unit]
	delta_val  = delta_func(value)
	delta_conf = { delta_key: delta_val }
	delta      = timedelta(**delta_conf)
	begin_ts   = datetime.fromtimestamp(begin)

	if verbose: print(f"{value=} {unit=} {begin=} {after=} {delta_key=} {delta_val=} {delta_conf=} {delta=} {begin_ts=}")

	if after:
		ts = int( datetime.timestamp(begin_ts + delta) )
	else:
		ts = int( datetime.timestamp(begin_ts - delta) )

	if verbose: print(f"{value=} {unit=} {begin=} {after=} {delta_key=} {delta_val=} {delta_conf=} {delta=} {begin_ts=} {ts=} {datetime.fromtimestamp(ts)}")

	return ts





def validate_time(vals: str) -> str:
	if vals is None: return None

	assert isinstance(vals, str)

	assert len(vals) >= 2

	unit = vals[-1]

	assert unit in delta_short_to_long, f"invalide unit: {unit} not int {', '.join(delta_short_to_long.keys())}"

	val  = int(vals[:-1])

	assert val > 0

	return vals



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
		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		sel = select(cls)
		qry = sel.offset(self.offset).limit(self.limit)
		return qry

	@classmethod
	def endpoints(cls):
		return {}

	def gen_html_filters(self):
		raise NotImplementedError()

SharedFilterQuery = Annotated[SharedFilterQueryParams, Depends(SharedFilterQueryParams)]





class TimedFilterQueryParams(SharedFilterQueryParams):
	since      : Annotated[Optional[int]  , Query(default=Depends(get_since), ge=0)       ]
	until      : Annotated[Optional[int]  , Query(default=None              , ge=0)       ]
	time_from  : Annotated[Optional[str]  , Query(default=None                    ), AfterValidator(validate_time) ]
	time_length: Annotated[Optional[str]  , Query(default=None                    ), AfterValidator(validate_time) ]

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = SharedFilterQueryParams.__call__(self, session, cls)

		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		if self.since is not None:
			print(" SINCE", self.since, type(self.since))
			qry = qry.where(cls.gateway_receive_time >= self.since)

		if self.until is not None:
			print(" UNTIL", self.until)
			qry = qry.where(cls.gateway_receive_time <= self.until)

		if self.time_from is not None:
			print(" TIME_FROM", self.time_from)
			time_from      = self.time_from
			assert len(time_from) >= 2

			time_from_unit = time_from[-1]
			time_from_val  = int(time_from[:-1])

			assert time_from_unit in delta_short_to_long, f"invalide unit: {delta_short_to_long.keys()}"

			time_from_ts   = get_timestamp(value=time_from_val, unit=time_from_unit, begin=None, after=False)

			qry            = qry.where(cls.gateway_receive_time >= time_from_ts)

			if self.time_length is not None:
				print(" TIME_LENGTH", self.time_length)
				time_length      = self.time_length
				assert len(time_length) >= 2

				time_length_unit = time_length[-1]
				time_length_val  = time_length[:-1]
				assert time_length_unit in delta_short_to_long, f"invalide unit: {delta_short_to_long.keys()}"

				time_length_ts   = get_timestamp(value=time_length_val, unit=time_length_unit, begin=time_from_ts, after=True)
				qry              = qry.where(cls.gateway_receive_time <= time_length_ts)

		return qry

	@classmethod
	def endpoints(cls):
		return {
			**{
				"since"      : ("since"      , int  , False),
				"until"      : ("until"      , int  , False),
				"time_from"  : ("time_from"  , str  , False),
				"time_length": ("time_length", str  , False),
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
