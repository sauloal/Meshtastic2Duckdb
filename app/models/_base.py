import sys
import json
import typing
import dataclasses

from typing import Annotated, Optional

from sqlalchemy             import BigInteger, SmallInteger, Integer, Text, Float, Boolean, LargeBinary
# from sqlalchemy.orm         import Mapped
# from sqlalchemy.orm         import mapped_column
# from sqlalchemy.orm         import registry

from fastapi import Depends, Query

import pydantic
from pydantic import BaseModel

from typing import Annotated, Generator, Literal

from sqlmodel import Field, Sequence, SQLModel, Column
from sqlmodel import select, Session
#, SQLModel, create_engine

#from sqlalchemy import Sequence

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
	@classmethod
	def _parse_fields(cls, packet):
		try:
			return { k: v(packet) for k,v in cls._shared_fields + cls._fields }
		except KeyError as e:
			print(packet)
			raise e

	@classmethod
	def from_packet(cls, packet):
		fields  = cls._parse_fields(packet)

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



def gen_id_seq(name:str):
	id_seq = Sequence(f"{name.lower()}_id_seq")
	Sequences.append( id_seq )
	#field  = Field(Column(BigInteger, id_seq, server_default=id_seq.next_value(), primary_key=True), primary_key=True, sa_column_kwargs={"server_default": id_seq.next_value()})
	#return field
	return id_seq





# https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#classes-as-dependencies_1
class SharedFilterQueryParams(BaseModel):
	offset  : Annotated[int       , Query(default=0  , ge=0)        ]
	limit   : Annotated[int       , Query(default=100, gt=0, le=100)]
	q       : Annotated[str | None, Query(default=None)             ]
	dryrun  : Annotated[bool      , Query(default=False)            ]
	# order_by: Literal["created_at", "updated_at"] = "created_at"
	# group_by: Literal["created_at", "updated_at"] = "created_at"
	# tags    : list[str] = []

SharedFilterQuery = Annotated[SharedFilterQueryParams, Depends(SharedFilterQueryParams)]


from datetime import datetime
def get_now():
	return datetime.timestamp(datetime.now())

def get_since():
	return datetime.timestamp(datetime.now() - datetime.timedelta(days=1))

class TimedFilterQueryParams(SharedFilterQueryParams):
	since   : Annotated[int       , Query(default_factory=get_since, ge=0)       ]
	until   : Annotated[int       , Query(default_factory=get_now  , ge=0)       ]

TimedFilterQuery = Annotated[TimedFilterQueryParams, Depends(TimedFilterQueryParams)]
