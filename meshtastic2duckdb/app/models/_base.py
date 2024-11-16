import sys
import json
import typing
import datetime
import dataclasses

from typing import Annotated, Optional, Generator, Literal

from sqlalchemy             import BigInteger, SmallInteger, Integer, Text, Float, Boolean, LargeBinary

from fastapi import Depends, Query
from fastapi import HTTPException

import pydantic
from pydantic import BaseModel

from sqlmodel import Field, Sequence, SQLModel, Column, Session

from ._query import SharedFilterQuery, SharedFilterQueryParams, TimedFilterQuery, TimedFilterQueryParams
from .. import dbgenerics

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

	@classmethod
	def _parse_fields(cls, packet) -> dict[str, typing.Any]:
		try:
			return { k: v(packet) for k,v in cls._shared_fields + cls._fields }
		except KeyError as e:
			print(packet)
			raise e

	@classmethod
	def from_packet(cls, packet) -> "ModelBaseClass":
		fields  = cls._parse_fields(packet)
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

	def toORM(self) -> "ModelBase":
		orm_class = self.__class__.__ormclass__()
		# print("orm_class", orm_class)

		orm_inst       = orm_class(**self.toDICT())
		# print("orm_inst      ", orm_inst)

		return orm_inst



class ModelBase:
	gateway_receive_time : int64 = Field(              sa_type=BigInteger()  , nullable=False, index=True )

	@classmethod
	def Query( cls, *, session_manager: dbgenerics.GenericSessionManager, query_filter: SharedFilterQuery ) -> "list[ModelBase]":
		#print("ModelBase: class query", "model", cls, "session_manager", session_manager, "query_filter", query_filter)
		# https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes

		with session_manager as session:
			qry     = query_filter(session, cls)
			results = session.exec(qry)
			results = [r.to_dataclass() for r in results]
		return results

	@classmethod
	def from_dataclass(cls, inst: ModelBaseClass) -> "Message":
		return cls(**inst.toJSON())

	def to_dataclass(self) -> ModelBaseClass:
		return self.__class__.__dataclass__()(**self.model_dump())

		#return self.__class__.__dataclass(**self.model_dump())
		#return cls(**self.model_dump())

	@classmethod
	def register(cls, prefix: str, gen_endpoint, status, db_ro, db_rw):
		name      = cls.__name__
		nick      = name.lower()
		filters   = cls.__filter__()
		data_cls  = cls.__dataclass__()
		filter_by = filters.endpoints()

		endpoints = { "endpoints": ["", "list"] + list(filter_by.keys()) }

		prefix_u  = f"{prefix}/{nick}"

		if True:
			gen_endpoint(verb="GET",  endpoint=f"{prefix_u}",                                   response_model=dict[str, list[str]], fixed_response=endpoints,                                      name=f"{name} Get",                       summary=f"Get {name} Endpoints",             description="Get {name} Endpoints",             tags=[name], filter_key=None,      filter_is_list=False,   model=cls, session_manager_t=db_ro)
			gen_endpoint(verb="POST", endpoint=f"{prefix_u}",                                   response_model=None,                 fixed_response=None,      status_code=status.HTTP_201_CREATED, name=f"{name} Add",                       summary=f"Add {name}",                       description="Add {name}",                       tags=[name], filter_key=None,      filter_is_list=False,   model=cls, session_manager_t=db_rw)

			gen_endpoint(verb="GET",  endpoint=f"{prefix_u}/list",                              response_model=list[data_cls],       fixed_response=None,      status_code=None,                    name=f"{name} List",                      summary=f"Get {name} List",                  description="Get {name} List",                  tags=[name], filter_key=None,      filter_is_list=False,   model=cls, session_manager_t=db_ro)


		for filter_endpoint, (attr_name, filter_type, is_list) in filter_by.items():
			filter_endpoint_str = filter_endpoint.replace('-', ' ')
			gen_endpoint(verb="GET" , endpoint=f"{prefix_u}/{filter_endpoint}/{{{attr_name}}}", response_model=list[data_cls],       fixed_response=None,      status_code=None,                    name=f"{name} Get {filter_endpoint_str}", summary=f"Get {name} {filter_endpoint_str}", description="Get {name} {filter_endpoint_str}", tags=[name], filter_key=attr_name, filter_is_list=is_list, model=cls, session_manager_t=db_ro)



def gen_id_seq(name:str) -> Sequence:
	id_seq = Sequence(f"{name.lower()}_id_seq")
	Sequences.append( id_seq )
	#field  = Field(Column(BigInteger, id_seq, server_default=id_seq.next_value(), primary_key=True), primary_key=True, sa_column_kwargs={"server_default": id_seq.next_value()})
	#return field
	return id_seq


