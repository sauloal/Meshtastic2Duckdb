import sys
import json
import typing
import datetime
import dataclasses

from typing     import Annotated, Optional, Generator, Literal

from sqlalchemy import BigInteger, SmallInteger, Integer, Text, Float, Boolean, LargeBinary

from fastapi    import FastAPI, Depends, Query
from fastapi    import HTTPException

import pydantic
from pydantic   import BaseModel

from sqlmodel   import Field, Sequence, SQLModel, Column, Session, or_

from ._query    import SharedFilterQuery, SharedFilterQueryParams, TimedFilterQuery, TimedFilterQueryParams, gen_html_filters
from .          import _converters as converters
from ..         import dbgenerics

# https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html

#https://www.postgresql.org/docs/current/datatype-numeric.html
#smallint  2 bytes  small-range integer	                      -32768 to               +32767
#integer   4 bytes  typical choice for integer 	         -2147483648 to          +2147483647
#bigint    8 bytes  large-range integer	        -9223372036854775808 to +9223372036854775807

#intpk = Annotated[int, mapped_column(init=False, primary_key=True)]
int8  = Annotated[int, SmallInteger] # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.SMALLINT
int16 = Annotated[int, SmallInteger]
int32 = Annotated[int, Integer     ] # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.INT
int64 = Annotated[int, BigInteger  ] # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.BIGINT

# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapping-multiple-type-configurations-to-python-types


Sequences = []


class ModelBaseClass(pydantic.BaseModel):
	gateway_receive_time : int64

	__pretty_names__ = {
		"gateway_receive_time": (0,"Gateway Receive Time", converters.epoch_to_str)
	}

	@classmethod
	def _parse_fields(cls, packet) -> dict[str, typing.Any]:
		try:
			return { (0,k): v(packet) for k,v in cls._shared_fields + cls._fields }
		except KeyError as e:
			print(packet)
			raise e

	@classmethod
	def from_packet(cls, packet) -> "ModelBaseClass":
		fields  = { k:v for (_,k),v in cls._parse_fields(packet).items() }
		fields["gateway_receive_time"] = int(datetime.datetime.timestamp(datetime.datetime.now()))

		try:
			inst    = cls(**fields)
		except Exception as e:
			print("cls           ", cls               , file=sys.stderr)
			print("fields        ", fields            , file=sys.stderr)
			print("_shared_fields", cls._shared_fields, file=sys.stderr)
			print("_fields       ", cls._fields       , file=sys.stderr)
			print("packet        ", packet            , file=sys.stderr)
			raise KeyError from e

		return inst

	def toJSON(self) -> str:
		d = self.toDICT()
		j = json.dumps(d)
		return j

	def toDICT(self) -> dict[str, typing.Any]:
		d = {k:v for k,v in self if k not in ["id", "metadata"]}
		return d

	def model_pretty_dump(self):
		#print("model_pretty_dump", self)
		return { self.__pretty_names__.get(k, (99,k,converters.echo)): v for k,v in self.model_dump().items() }

	def toORM(self) -> "ModelBase":
		orm_class = self.__class__.__ormclass__()
		# print("orm_class", orm_class)

		orm_inst       = orm_class(**self.toDICT())
		# print("orm_inst      ", orm_inst)

		return orm_inst



class ModelBase:
	gateway_receive_time : int64 = Field(              sa_type=BigInteger()  , nullable=False, index=True )

	@classmethod
	def Query( cls, *, session_manager: dbgenerics.GenericSessionManager, query_filter: SharedFilterQuery, filter_is_unique: str|None = None ) -> "list[ModelBase]":
		print("ModelBase: class query", "model", cls, "session_manager", session_manager, "query_filter", query_filter, "filter_is_unique", filter_is_unique)
		# https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes

		with session_manager as session:
			qry     = query_filter(session, cls, filter_is_unique=filter_is_unique)
			results = session.exec(qry)
			results = [r.to_dataclass() if hasattr(r, "to_dataclass") else r for r in results]

		return results

	@classmethod
	def from_dataclass(cls, inst: ModelBaseClass) -> "Message":
		return cls(**inst.toJSON())

	def to_dataclass(self) -> ModelBaseClass:
		return self.__class__.__dataclass__()(**self.model_dump())

		#return self.__class__.__dataclass(**self.model_dump())
		#return cls(**self.model_dump())

	@classmethod
	def register(cls, app: FastAPI, prefix: str, gen_endpoint, status, db_ro, db_rw):
		name      = cls.__name__
		filters   = cls.__filter__()
		data_cls  = cls.__dataclass__()

		nick      = name.lower()
		filter_by = filters.endpoints()
		fields    = cls.model_fields
		tags      = [f"/api/messages/{name.lower()}"]

		endpoints = { "endpoints": ["", "list"] + list(filter_by.keys()) }

		prefix_u  = f"{prefix}/{nick}"

		if True:
			gen_endpoint(
				app               = app,
				verb              = "GET",
				endpoint          = f"{prefix_u}",
				response_model    = dict[str, list[str]],
				fixed_response    = endpoints,
				name              = f"api_{name}_get".lower().replace(" ","_"),
				summary           = f"Get {name} Endpoints",
				description       =  "Get {name} Endpoints",
				tags              = tags,
				filter_key        = None,
				filter_is_list    = False,
				model             = cls,
				session_manager_t = db_ro
			)
			gen_endpoint(
				app               = app,
				verb              = "POST",
				endpoint          = f"{prefix_u}",
				response_model    = None,
				fixed_response    = None,
				status_code       = status.HTTP_201_CREATED,
				name              = f"api_{name}_add".lower().replace(" ","_"),
				summary           = f"Add {name}",
				description       =  "Add {name}",
				tags              = tags,
				filter_key        = None,
				filter_is_list    = False,
				model             = cls,
				session_manager_t = db_rw
			)

			gen_endpoint(
				app               = app,
				verb              = "GET",
				endpoint          = f"{prefix_u}/list",
				response_model    = list[data_cls],
				fixed_response    = None,
				status_code       = None,
				name              = f"api_{name}_list".lower().replace(" ","_"),
				summary           = f"Get {name} List",
				description       =  "Get {name} List",
				tags              = tags,
				filter_key        = None,
				filter_is_list    = False,
				model             = cls,
				session_manager_t = db_ro
			)


		filters = [ fe for fe in filter_by.keys() ]
		gen_endpoint(
				app               = app,
				verb              = "GET",
				endpoint          = f"{prefix_u}/filters",
				response_model    = list[str],
				fixed_response    = filters,
				status_code       = None,
				name              = f"api_{name}_get_filters".lower().replace(" ","_"),
				summary           = f"Get {name} Filters",
				description       =  "Get {name} Filters",
				tags              = tags,
				filter_key        = None,
				filter_is_list    = False,
				model             = cls,
				session_manager_t = db_ro
		)

		for filter_endpoint, (attr_name, filter_type, is_list) in filter_by.items():
			filter_endpoint_str = filter_endpoint.replace('-', ' ')
			gen_endpoint(
				app               = app,
				verb              = "GET",
				endpoint          = f"{prefix_u}/filters/{filter_endpoint}/{{{attr_name}}}",
				response_model    = list[data_cls],
				fixed_response    = None,
				status_code       = None,
				name              = f"api_{name}_get_filters_{filter_endpoint_str}".lower().replace(" ","_"),
				summary           = f"Get {name} {filter_endpoint_str}",
				description       =  "Get {name} {filter_endpoint_str}",
				tags              = tags,
				filter_key        = attr_name,
				filter_is_list    = is_list,
				model             = cls,
				session_manager_t = db_ro
			)


		uniques = [ un for un in fields.keys() ]
		gen_endpoint(
				app               = app,
				verb              = "GET",
				endpoint          = f"{prefix_u}/uniques",
				response_model    = list[str],
				fixed_response    = uniques,
				status_code       = None,
				name              = f"api_{name}_get_uniques".lower().replace(" ","_"),
				summary           = f"Get {name} Uniques",
				description       =  "Get {name} Uniques",
				tags              = tags,
				filter_key        = None,
				filter_is_list    = False,
				model             = cls,
				session_manager_t = db_ro
		)

		for field in uniques:
			gen_endpoint(
				app               = app,
				verb              = "GET",
				endpoint          = f"{prefix_u}/uniques/{field}",
				response_model    = list[typing.Any],
				fixed_response    = None,
				status_code       = None,
				name              = f"api_{name}_get_uniques_{field}".lower().replace(" ","_"),
				summary           = f"Get {name} Uniques {field}",
				description       =  "Get {name} Uniques {field}",
				tags              = tags,
				filter_key        = None,
				filter_is_list    = False,
				model             = cls,
				session_manager_t = db_ro,
				filter_is_unique  = field
			)



def gen_id_seq(name:str) -> Sequence:
	id_seq = Sequence(f"{name.lower()}_id_seq")
	Sequences.append( id_seq )
	#field  = Field(Column(BigInteger, id_seq, server_default=id_seq.next_value(), primary_key=True), primary_key=True, sa_column_kwargs={"server_default": id_seq.next_value()})
	#return field
	return id_seq


