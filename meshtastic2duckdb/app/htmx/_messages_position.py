from ._router   import *
from ._messages import *


@router.get("/messages/position")
async def mx_messages_position(request: Request, response: Response, session_manager: db.SessionManagerDepRO, query_filter: models.Position.__filter__(),
	image_width: QueryImageDimension = 500, image_height: QueryImageDimension = 250, bar_width: QueryBarWidth=0.8):

	title			= "Position"
	target                  = "container"

	urls			= get_urls()
	root			= urls[title]

	cls                     = models.Position

	url_self                = root
	url_opts                = {k:v for k,v in query_filter.model_dump().items() if v is not None}

	html_filters            = query_filter.gen_html_filters(url_self, lambda column: cls.Query(session_manager=session_manager, query_filter=query_filter, filter_is_unique=column))

	resp                    = cls.Query(session_manager=session_manager, query_filter=query_filter)
	count_all, count_filter = cls.Count(session_manager=session_manager, query_filter=query_filter)
	count_res               = len(resp)

	images                  = {}


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
	"""

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

			"extend"       : "partials/messages_position.html"
		}
	)

