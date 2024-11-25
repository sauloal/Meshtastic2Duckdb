from ._base    import *
from ._message import *
from fastapi   import params as fastapi_params

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

	__pretty_names__ = {
		**MessageClass.__pretty_names__,
		**{
			"user_id"   : (4, "User ID"       , converters.user_id),
			"longName"  : (4, "Long Name"     , converters.echo),
			"shortName" : (4, "Short Name"    , converters.echo),
			"macaddr"   : (4, "MAC Addr"      , converters.echo),
			"hwModel"   : (4, "Hardware Model", converters.echo),
			"role"      : (4, "Role"          , converters.echo),
			"publicKey" : (6, "Public Key"    , converters.echo),
		}
	}





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

	@classmethod
	def endpoints(cls):
		return {
			**{
				"by-user-id"   : ("userIds"   , str  , True),
				"by-short-name": ("shortNames", str  , True),
				"by-long-name" : ("longNames" , str  , True),
				"by-hw-model"  : ("hwModels"  , str  , True),
				"by-role"      : ("roles"     , Roles, True),
			},
			**TimedFilterQueryParams.endpoints()
		}

	def __call__(self, session: dbgenerics.GenericSession, cls):
		qry = TimedFilterQueryParams.__call__(self, session, cls)

		for k in self.model_fields.keys():
			v = getattr(self, k)
			if isinstance(v, fastapi_params.Depends):
				setattr(self, k, v.dependency())

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

	def gen_html_filters(self):
		#print("gen_html_filters :: SELF", self)
		return "gen_html_filters"
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
		</form>
		"""

NodeInfoFilterQuery = Annotated[NodeInfoFilterQueryParams, Depends(NodeInfoFilterQueryParams)]



"""
@app.get( "/api/messages/nodeinfo",                                summary = "Get NodeInfo Endpoints",       description = "Get NodeInfo Endpoints",    response_description = "NodeInfo Endpoints",    tags = ["NodeInfo"])
async def api_model_nodeinfo_get():
        return { "endpoints": ["list", "by-user-id", "by-long-name", "by-short-name", "by-hw-model", "by-role", "by-from-id", "by-from-node", "by-to-id", "by-to-node"] }

@app.post("/api/messages/nodeinfo",                                summary = "Add NodeInfo Instances",       description = "Add NodeInfo Instances",    response_description = "None",                  tags = ["NodeInfo"],    status_code = status.HTTP_201_CREATED)
async def api_model_nodeinfo_post(  data: models.NodeInfoClass,    session_manager: db.SessionManagerDepRW,  request: Request,                          response: Response ) -> None:
        return await api_model_post(data=data,                     session_manager=session_manager,          request=request,                           response=response )

@app.get( "/api/messages/nodeinfo/list",                           summary = "Get NodeInfo Instances",       description = "Get NodeInfo Instances",    response_description = "List of NodeInfo",      tags = ["NodeInfo"])
async def api_model_nodeinfo_list(                                 session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
        return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodeinfo/by-user-id/{user_id}",           summary = "Get NodeInfo Instances",       description = "Get NodeInfo Instances",    response_description = "List of NodeInfo",      tags = ["NodeInfo"])
async def api_model_nodeinfo_by_user_id(user_id: str,              session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
        query_filter.userIds = [user_id]
        return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodeinfo/by-long-name/{long_name}",       summary = "Get NodeInfo Instances",       description = "Get NodeInfo Instances",    response_description = "List of NodeInfo",      tags = ["NodeInfo"])
async def api_model_nodeinfo_by_long_name(long_name: str,          session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
        query_filter.longNames = [long_name]
        return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodeinfo/by-short-name/{short_name}",     summary = "Get NodeInfo Instances",       description = "Get NodeInfo Instances",    response_description = "List of NodeInfo",      tags = ["NodeInfo"])
async def api_model_nodeinfo_by_short_name(short_name: str,        session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
        query_filter.shortNames = [short_name]
        return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodeinfo/by-hw-model/{hw_model}",         summary = "Get NodeInfo Instances",       description = "Get NodeInfo Instances",    response_description = "List of NodeInfo",      tags = ["NodeInfo"])
async def api_model_nodeinfo_by_hw_model(hw_model: str,            session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
        query_filter.hwModels = [hw_model]
        return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )

@app.get( "/api/messages/nodeinfo/by-role/{role}",                 summary = "Get NodeInfo Instances",       description = "Get NodeInfo Instances",    response_description = "List of NodeInfo",      tags = ["NodeInfo"])
async def api_model_nodeinfo_by_role(role: str,                    session_manager: db.SessionManagerDepRO,  request: Request,                          response: Response,     query_filter: models.NodeInfo.__filter__() ) -> list[models.NodeInfoClass]:
        query_filter.roles = [role]
        return await api_model_get( model=models.NodeInfo,         session_manager=session_manager,          request=request,                           response=response,      query_filter=query_filter  )
"""

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
