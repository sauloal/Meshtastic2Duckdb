from ._router   import *
from ._messages import *


def lat_lon_stats(resp):
	lat_min, lat_max, lat_mid, lon_min, lon_max, lon_mid = None, None, None, None, None, None

	tracks = {}
	for r in resp:
		if r.latitude is not None:
			if lat_min is None: lat_min = r.latitude
			if lat_max is None: lat_max = r.latitude
			lat_min = r.latitude if r.latitude <= lat_min else lat_min
			lat_max = r.latitude if r.latitude >= lat_max else lat_max

		if r.longitude is not None:
			if lon_min is None: lon_min = r.longitude
			if lon_max is None: lon_max = r.longitude
			lon_min = r.longitude if r.longitude <= lon_min else lon_min
			lon_max = r.longitude if r.longitude >= lon_max else lon_max

		# TODO: calculate radius
		fromId = r.fromId.replace("!", "").replace("^", "")
		if r.latitude is not None and r.longitude is not None:
			tracks[fromId] = tracks.get(fromId, [[],[]])
			tracks[fromId][0].append( [r.longitude, r.latitude] )
			tracks[fromId][1].append( 10 )

	# TODO: fix negative numbers
	if lat_min is not None and lat_max is not None:
		lat_mid = (lat_max + lat_min) / 2.0
	else:
		lat_mid = 0.0

	if lon_min is not None and lon_max is not None:
		lon_mid = (lon_max + lon_min) / 2.0
	else:
		lon_mid = 0.0

	zoom     = 15
	max_zoom = 19

	return {
		"lat_min": lat_min,
		"lat_max": lat_max,
		"lat_mid": lat_mid,

		"lon_min": lon_min,
		"lon_max": lon_max,
		"lon_mid": lon_mid,

		"zoom"    : zoom,
		"max_zoom": max_zoom,
		"tracks"  : tracks,

		"colors"  : [ #https://github.com/pointhi/leaflet-color-markers
			["#2A81CB","#3274A3"],
			["#FFD326","#C1A32D"],
			["#CB2B3E","#982E40"],
			["#2AAD27","#31882A"],
			["#CB8427","#98652E"],
			["#9C2BCB","#742E98"],
			["#7B7B7B","#6B6B6B"],
			["#3D3D3D","#313131"],
		]
	}

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

	location_stats          = lat_lon_stats(resp)

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
			"title"         : title,
			"target"        : target,

			"urls"          : urls,
			"root"          : root,

			"count_all"     : count_all,
			"count_filter"  : count_filter,
			"count_res"     : count_res,

			"images"        : images,
			"location_stats": location_stats,

			"data"          : tuple(r.model_pretty_dump() for r in resp),
			"query_filter"  : query_filter,
			"html_filters"  : html_filters,
			"url_self"      : url_self,
			"url_opts"      : url_opts,

			#"calc_offset"   : calc_offset,

			"extend"        : "partials/messages_position.html"
		}
	)

