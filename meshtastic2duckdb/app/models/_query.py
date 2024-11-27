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





def gen_html_filters(inst, url: str, filter_opts: list[ tuple[str,str,str, list[tuple[str,str]]]] ) -> list[str]:
	res = []

	for name, label, field_type, values in filter_opts:
		if field_type == "select":
			val = f"""
			<label>{ label }</label>
			<select id="select-{name}"
				class="custom-select"
				name="{name}"
				autocomplete="off">
			"""

			if values is not None:
				for v_name, v_val in values:
					val += f"""<option value="{v_val}" """ + ("selected" if v_val == getattr(inst, name) else "") + f""">{v_name}</option>"""

					#elif hx_get is not None:
					#	val += f"""
					#	<option hx-get="{{{{ url_for("{hx_get}", **{self.as_js_dict()}) }}}}"></option>
					#"""

			val += """</select>"""

			res.append( val )
	return res






# https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#classes-as-dependencies_1
class SharedFilterQueryParams(BaseModel):
	offset  : Annotated[ int                  |None, Query(default= 0 , ge=0)         ]
	limit   : Annotated[ int                  |None, Query(default=10 , gt=0, le=100) ]
	#dryrun  : Annotated[ bool                 |None, Query(default=False)             ]
	order   : Annotated[ Literal["asc", "dsc"]|None, Query(default="asc")             ]
	# q       : Annotated[ str                  |None              , Query(default=None)              ]
	# reversed: Annotated[ bool                               , Query(default=False)             ]
	# order_by: Annotated[ Literal["created_at", "updated_at"], Query(default="created_at")      ]
	# group_by: Annotated[ Literal["created_at", "updated_at"], Query(default="created_at")      ]
	# tags    : list[str] = []

	# https://sqlmodel.tiangolo.com/tutorial/where/?h=select#where-and-expressions
	def __call__(self, session: dbgenerics.GenericSession, cls, filter_is_unique: str|None=None):
		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		for a in ["offset", "limit", "order"]:
			setattr(self, a, None if getattr(self, a) in ("",None) else getattr(self, a))



		if filter_is_unique: # get unique values
			print(f"FILTERING UNIQUE COLUMN: {filter_is_unique}")
			sel = select( getattr(cls, filter_is_unique) ).distinct()
		else:
			sel = select(cls)



		if self.order is not None:
			print(f" ORDER       '{self.order}'")
			if self.order == "asc":
				sel = sel.order_by( cls.gateway_receive_time.asc() )
			else:
				sel = sel.order_by( cls.gateway_receive_time.desc() )

		if self.offset is not None:
			print(f" OFFSET      '{self.offset}'")
			sel = sel.offset(self.offset)

		if self.limit  is not None:
			print(f" LIMIT       '{self.limit}'")
			sel = sel.limit(self.limit)

		return sel

	@classmethod
	def endpoints(cls):
		return {}

	def as_js_dict(self):
		res = ""
		for k in self.model_fields.keys():
			res = f""" "{k}": "{getattr(self, k)}"  """
		res = f"{{ {res} }}"
		return res

	def gen_html_filters(self, url):
		#print("gen_html_filters :: SELF", self)
		#filters = TimedFilterQueryParams.gen_html_filters(self, url, target=target)

		print(f"gen_html_filters: {self}")

		filter_opts = [
			[self, "order" , "Order" , "select", [
				["Ascending" ,"asc"],
				["Descending","dsc"]
			]],
			[self, "limit" , "Limit" , "select", [
				[ "10",  "10"],
				[ "25",  "25"],
				[ "50",  "50"],
				["100", "100"],
				["All", "1000000000"]
			]]
		]

		filters = []
		#filters.extend( gen_html_filters(self, url, filter_opts) )
		filters.extend( filter_opts )

		return filters

		"""
		<label>Year</label>
		<select id="select-year"
			class="custom-select"
			name="year"
			autocomplete="off"
			hx-get="{{ url_for(root) }}"
			hx-target="#container"
			hx-vals="js:{count: document.getElementById('count').value}">

			{% for year in years %}
				<option value="{{year}}"
				{% if year_selected == year %} selected {% endif %}>{{year}}</option>
			{% endfor %}
		</select>

		<hr/>

		<label>Count</label>
		<input  type="number"
			id="count"
			name="count"
			autocomplete="off"
			value="{{ count }}"
			hx-get="{{ url_for(root) }}"
			hx-target="#container"
			hx-vals="js:{year: document.getElementById('select-year').value}" />
		"""

SharedFilterQuery = Annotated[SharedFilterQueryParams, Depends(SharedFilterQueryParams)]





class TimedFilterQueryParams(SharedFilterQueryParams):
	since      : Annotated[Optional[int]  , Query(default=None              , ge=0)       ]
	until      : Annotated[Optional[int]  , Query(default=None              , ge=0)       ]
	# has precedence over since/until
	time_from  : Annotated[Optional[str]  , Query(default="1W"                    ), AfterValidator(validate_time) ]
	time_length: Annotated[Optional[str]  , Query(default="30Y"                   ), AfterValidator(validate_time) ]

	def __call__(self, session: dbgenerics.GenericSession, cls, filter_is_unique: str|None=None):
		qry = SharedFilterQueryParams.__call__(self, session, cls, filter_is_unique=filter_is_unique)

		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

		for a in ["since", "until", "time_from", "time_length"]:
			setattr(self, a, None if getattr(self, a) in ("",None) else getattr(self, a))

		if self.since is not None:
			if self.time_from is None:
				print(f" SINCE       '{self.since}' {type(self.since)}")
				qry = qry.where(cls.gateway_receive_time >= self.since)

		if self.until is not None:
			if self.time_length is None:
				print(f" UNTIL       '{self.until}'")
				qry = qry.where(cls.gateway_receive_time <= self.until)

		if self.time_from is not None:
			print(f" TIME_FROM   '{self.time_from}'")
			time_from      = self.time_from
			assert len(time_from) >= 2

			time_from_unit =     time_from[ -1]
			time_from_val  = int(time_from[:-1])

			assert time_from_unit in delta_short_to_long, f"invalide unit: {delta_short_to_long.keys()}"

			time_from_ts   = get_timestamp(value=time_from_val, unit=time_from_unit, begin=None, after=False)

			qry            = qry.where(cls.gateway_receive_time >= time_from_ts)

			if self.time_length is not None:
				print(f" TIME_LENGTH '{self.time_length}'")
				time_length      = self.time_length
				assert len(time_length) >= 2

				time_length_unit =     time_length[ -1]
				time_length_val  = int(time_length[:-1])
				assert time_length_unit in delta_short_to_long, f"invalide unit: {delta_short_to_long.keys()}"

				time_length_ts   = get_timestamp(value=time_length_val, unit=time_length_unit, begin=time_from_ts, after=True)
				qry              = qry.where(cls.gateway_receive_time <= time_length_ts)

		return qry

	def gen_html_filters(self, url):
		#print("gen_html_filters :: SELF", self)

		filter_opts = [
			#["since"      , "Since" , "select",  None],
			#["until"      , "Until" , "select",  None],
			[self, "time_from"  , "From"  , "select", [
					[ "1 Day"   ,  "1D"],
					[ "3 Days"  ,  "3D"],
					[ "1 Week"  ,  "1W"],
					[ "2 Weeks" ,  "2W"],
					[ "1 Month" ,  "1M"],
					[ "3 Months",  "3M"],
					[ "6 Months",  "6M"],
					[ "1 Years" ,  "1Y"],
					[ "Forever" , "30Y"],
				]
			],
			[self, "time_length", "Length", "select", [
					[ "1 Hour"  ,  "1h"],
					[ "3 Hours" ,  "3h"],
					[ "6 Hours" ,  "6h"],
					["12 Hours" , "12h"],
					[ "1 Day"   ,  "1D"],
					[ "3 Days"  ,  "3D"],
					[ "1 Week"  ,  "1W"],
					[ "2 Weeks" ,  "2W"],
					[ "1 Month" ,  "1M"],
					[ "3 Months",  "3M"],
					[ "6 Months",  "6M"],
					[ "1 Years" ,  "1Y"],
					[ "Forever" , "30Y"],
				]
			]
		]

		filters     = SharedFilterQueryParams.gen_html_filters(self, url)
		#filters.extend( gen_html_filters(self, url, filter_opts) )
		filters.extend( filter_opts )

		return filters

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
