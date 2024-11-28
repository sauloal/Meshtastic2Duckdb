from ._router   import *
from ._messages import *


@router.get("/messages/nodeinfo")
async def mx_messages_nodeinfo(request: Request, response: Response, session_manager: db.SessionManagerDepRO, query_filter: models.NodeInfo.__filter__(),
	image_width: QueryImageDimension = 500, image_height: QueryImageDimension = 250, bar_width: QueryBarWidth=0.8):

	"""
	print(f"mx_charts_temp {year=} {count=} {image_width=} {image_height=} {bar_width=} {session_manager=}")
	# models.register(api_router, prefix="/messages", status=status, db=db)
	# def gen_endpoint(*, app: FastAPI, verb: str, endpoint: str, name: str, summary: str, description: str, model: Message, session_manager_t, tags: list[str], filter_key:str=None, filter_is_list: bool=False, response_model=None, fixed_response=None, status_code=None):
	# async def endpoint(                             session_manager: session_manager_t, request: Request, response: Response, query_filter: query_filter, path_param: str = Path(alias=alias)) -> response_model:
	# NodeInfo   .register(app=app, prefix=prefix, gen_endpoint=gen_endpoint, status=status, db_ro=db.SessionManagerDepRO, db_rw=db.SessionManagerDepRW)
	# def register(cls, app: FastAPI, prefix: str, gen_endpoint, status, db_ro, db_rw):
	# resp = model.Query(session_manager=session_manager, query_filter=query_filter)

	# , query_filter: query_filter
	#data_class, query_filter = models._gen.init_model(model=model, session_manager_t=session_manager_t)

	@classmethod
	def Query( cls, *, session_manager: dbgenerics.GenericSessionManager, query_filter: SharedFilterQuery ) -> "list[ModelBase]":
		#print("ModelBase: class query", "model", cls, "session_manager", session_manager, "query_filter", query_filter)
		# https://fastapi.tiangolo.com/tutorial/sql-databases/#read-heroes

		with session_manager as session:
			qry     = query_filter(session, cls)
			results = session.exec(qry)
			results = [r.to_dataclass() for r in results]
		return results
	"""

	title			= "Node Info"
	target                  = "container"

	urls			= get_urls()
	root			= urls[title]

	cls                     = models.NodeInfo

	url_self                = root
	url_opts                = {k:v for k,v in query_filter.model_dump().items() if v is not None}

	html_filters            = query_filter.gen_html_filters(url_self, lambda column: cls.Query(session_manager=session_manager, query_filter=query_filter, filter_is_unique=column))

	resp                    = cls.Query(session_manager=session_manager, query_filter=query_filter)
	count_all, count_filter = cls.Count(session_manager=session_manager, query_filter=query_filter)
	count_res               = len(resp)


	"""
	def calc_offset(url, url_for, offset):
		up = { k:v for k,v in url_opts.items() }
		up["offset" ] = offset
		return url_for(url, "name").include_query_params(**up)
	"""

	images                  = {
		"Rx Rssi": gen_image(
			**gen_image_data(resp, "rxTime", ["rxRssi"] ),
			image_height	= image_height,
			image_width	= image_width,
			bar_width	= bar_width,
			title		= f"Rx Rssi through time ({count_res:,d}/{count_filter:,d}/{count_all:,d})",
			x_label		= "Time",
			y_label		= "Rx Rssi",
			graph_type 	= "multiline"
		),
		"Rx Snr": gen_image(
			**gen_image_data(resp, "rxTime", ["rxSnr"] ),
			image_height	= image_height,
			image_width	= image_width,
			bar_width	= bar_width,
			title		= f"Rx Snr through time ({count_res:,d}/{count_filter:,d}/{count_all:,d})",
			x_label		= "Time",
			y_label		= "Rx Snr",
			graph_type 	= "multiline"
		)
	}

	return templates.TemplateResponse(
		request = request,
		name    = "index_home.html",
		context = {
			"title"        : title,
			"target"       : target,

			"urls"         : urls,
			"root"         : root,

			"count_all"    : count_all,
			"count_filter" : count_filter,
			"count_res"    : count_res,

			"images"       : images,

			"data"         : tuple(r.model_pretty_dump() for r in resp),
			"query_filter" : query_filter,
			"html_filters" : html_filters,
			"url_self"     : url_self,
			"url_opts"     : url_opts,

			#"calc_offset"  : calc_offset,

			"extend"       : "partials/nodeinfo.html"
		}
	)

