import datetime

from fastapi            import FastAPI, APIRouter, Request, Response, Path, Query, Depends
from fastapi            import status

from fastapi.templating import Jinja2Templates
from fastapi.responses  import HTMLResponse

from pydantic.functional_validators import AfterValidator
from typing_extensions              import Annotated

# https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates
#
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-bar-charts/
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-line-charts/
# https://github.com/bugbytes-io/django-htmx-bokeh/tree/barchart
# https://github.com/ocramz/htmx-plotly
# https://htmx.org/examples/lazy-load/





router    = APIRouter(tags=["HTMX"], include_in_schema=False, default_response_class=HTMLResponse)

templates = Jinja2Templates(directory="templates")

templates.env.filters["format_integer"] = lambda x: f"{x:,d}"



def year_get_min():
	return 2023

def year_get_max():
	return 2024

def validate_year(year: int) -> int:
	assert year >= year_get_min()
	assert year <= year_get_max()
	return year

def get_urls():
	return {
		"Home"     : "mx_start",
		"Node Info": "mx_charts_nodeinfo"
	}



QueryYear  = Annotated[int | None, AfterValidator(validate_year),  Query(default_factory=year_get_max)]
QueryCount = Annotated[int | None, Query(ge=5, le=1_000)]




@router.get("/")
async def mx_root(request: Request):
	urls          = get_urls()
	title         = "Home"
	root          = urls[title]

	return templates.TemplateResponse(
		request=request, name="index.html", context={
			"title"        : title,
			"root"         : root,
			"urls"         : urls,
		}
	)

@router.get("/start")
async def mx_start(request: Request):
	urls          = get_urls()
	title         = "Home"
	root          = urls[title]

	return templates.TemplateResponse(
		request=request, name="partials/start.html", context={
			"title"        : title,
			"root"         : root,
		}
	)





from bokeh.models   import PrintfTickFormatter, DatetimeTickFormatter
from bokeh.models   import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed    import components
import math


def gen_image(labels: list[str], values: list[int | float] | list[list[int|float]], title: str, x_label: str, y_label: str, image_height: int=500, image_width: int=500, bar_width: float=0.8, graph_type: str="vbar") -> tuple[str,str]:
	# https://docs.bokeh.org/en/2.4.1/docs/reference/colors.html#bokeh-colors-named
	COLORS          = ['red', 'orangered', 'orange', 'hotpink', 'blueviolet', 'gold', 'brown', 'deepskyblue', 'blue', 'cyan', 'green', 'limegreen', 'dimgray', 'black']

	title_align     = 'center'
	title_font_size = '1.5em'

	if graph_type in ("vbar", "hbar", "line", "scatter"):
		cds                      = ColumnDataSource( data={x_label: labels, y_label: values} )

		fig                      = figure(x_range=labels, height=image_height, width=image_width, title=title)
		#fig.title.align          = title_align
		#fig.title.text_font_size = title_font_size
		#fig.legend.location      = 'top_left'
		#fig.yaxis[0].formatter   = NumeralTickFormatter(format="$0.0a")
		#fig.xaxis.major_label_orientation = math.pi / 4

		if   graph_type == "vbar":    # vertical bar chart
			fig.vbar(   x=x_label, top=y_label, width=bar_width, source=cds)

		elif graph_type == "hbar":    # horizontal bar chart
			fig.hbar(   x=x_label, top=y_label, width=bar_width, source=cds)

		elif graph_type == "line":    # line chart
			fig.line(   x=x_label, top=y_label, width=bar_width, source=cds, line_width=2)

		elif graph_type == "scatter": # scatter plot
			fig.scatter(x=x_label, top=y_label, width=bar_width, source=cds)

		else:
			raise ValueError(f"unknown graph type: {graph_type}")

		if isinstance(values[0], datetime.datetime):
			fig.xaxis[0].formatter   = DatetimeTickFormatter(days="%Y/%m/%d %H:%M", hours="%Y/%m/%d %H:%M", minutes="%Y/%m/%d %H:%M")

	elif graph_type in ("multiline",):
		#labels [a,b,c]
		#values [[0,1],[2,3]]
		#print(f"gen_image {labels=}")
		#print(f"gen_image {values=}")

		cds = ColumnDataSource(data=dict(
			xs     = values[0],
			ys     = values[1],
			names  = labels,
			colors = COLORS[:len(labels)]
			#country_years = year_data,
			#country_gdps  = gdp_data,
			#names         = c,
			#colors        = ['red', 'blue', 'green']
		))

		fig                      = figure(height=image_height, width=image_width, title=title)

		fig.multi_line(
			source       = cds,
			xs           = 'xs',
			ys           = 'ys',
			legend_group = 'names',
			line_color   = 'colors',
			line_width   = 2,
		)

		if isinstance(values[0][0][0], datetime.datetime):
			#print("IS DATETIME")
			fig.xaxis[0].formatter   = DatetimeTickFormatter(days="%Y/%m/%d %H:%M", hours="%Y/%m/%d %H:%M", minutes="%Y/%m/%d %H:%M")

	else:
		raise ValueError(f"Unknown graph type: {graph_type}")

	fig.title.align                   = title_align
	fig.title.text_font_size          = title_font_size
	fig.legend.location               = 'top_right'
	fig.xaxis.major_label_orientation = math.pi / 4

	script, div = components(fig)

	return { "script": script, "div": div }

"""
	# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-line-charts/
	# These will be our parent lists, containing country-specific lists as elements
	year_data = []
	gdp_data  = []

	# we define 3 countries for the multi-line chart
	c = ['Germany', 'China', 'France']

	# for each country, we get the relevant data from DB, and add to parent lists
	for country in c:
		gdps = GDP.objects.filter(country=country).order_by('year')
		year_data.append([d.year for d in gdps])
		gdp_data .append([d.gdp  for d in gdps])


	cds = ColumnDataSource(data=dict(
		country_years = year_data,
		country_gdps  = gdp_data,
		names         = c,
		colors        = ['red', 'blue', 'green']
	))

	# create a figure, and add styles
	fig                      = figure(height=500, title=f"{country} GDP")
	fig.title.align          = 'center'
	fig.title.text_font_size = '1.5em'
	fig.yaxis[0].formatter   = NumeralTickFormatter(format="$0.0a")

	# call the figure's .multi_line() function and pass CDS fields
	# we add legend group and color data to differentiate the lines!
	# https://docs.bokeh.org/en/3.0.1/docs/examples/plotting/multi_line.html
	fig.multi_line(
		source       = cds,
		xs           = 'country_years',
		ys           = 'country_gdps',
		line_width   = 2,
		legend_group = 'names',
		line_color   = 'colors'
	)
"""

"""
	script, div		= gen_image(
		labels		= labels,
		values		= values,
		title		= f"Temperature through time ({count} samples) : Year {year}",
		x_label		= "Date",
		y_label		= "Temperature",
		image_height	= image_height,
		image_width	= image_width,
		bar_width	= bar_width,
		graph_type 	= "vbar"
	)
"""




QueryImageDimension  = Annotated[int   | None, Query(ge=100, le=10_000)]
QueryBarWidth        = Annotated[float | None, Query(ge=0.1, le=1.0   )]



from .. import db
from .. import models

def gen_image_data(resp, x_name, y_names ):
	resp_dict = {}

	for r in resp:
		k = r.longName
		resp_dict[k] = resp_dict.get(k, [])

		if len(resp_dict[k]) == 0:
			for l in range(len(y_names)+1):
				resp_dict[k].append([])

		# Assumes X is always time
		resp_dict[k][0].append( datetime.datetime.utcfromtimestamp( getattr(r, x_name) ) )
		for y_pos, y_name in enumerate(y_names):
			resp_dict[k][y_pos+1].append( getattr(r, y_name) )

	# assumes multiline
	labels = sorted(resp_dict.keys())
	values = tuple( tuple(resp_dict[k][i] for k in sorted(resp_dict.keys())) for i in range(len(y_names) + 1) )

	return { "labels": labels, "values": values }


@router.get("/charts/nodeinfo")
async def mx_charts_nodeinfo(request: Request, response: Response, year: QueryYear, session_manager: db.SessionManagerDepRO, query_filter: models.NodeInfo.__filter__(),
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

	urls			= get_urls()
	title			= "Node Info"
	root			= urls[title]
	years			= list( range(year_get_min(), year_get_max()+1) )

	#labels			= list( str(v) for v in range(1, count+1) )
	#values			= list(                 range(1, count+1))

	cls                     = models.NodeInfo
	#query_filter_cls        = cls.get_filter_class()
	#data_class, query_filter_cls = models._gen.init_model(model=cls, session_manager_t=session_manager)
	#print(query_filter)

	url_self                = "mx_charts_nodeinfo"
	url_opts                = {k:v for k,v in query_filter.model_dump().items() if v is not None}

	target                  = "#container"
	html_filters            = query_filter.gen_html_filters(url_self, lambda column: cls.Query(session_manager=session_manager, query_filter=query_filter, filter_is_unique=column))
	print("query_filter", type(query_filter), query_filter, type(html_filters), html_filters)

	resp                    = cls.Query(session_manager=session_manager, query_filter=query_filter)
	count_all, count_filter = cls.Count(session_manager=session_manager, query_filter=query_filter)
	count_res               = len(resp)
	#print( resp )

	def calc_offset(url, url_for, offset):
		up = { k:v for k,v in url_opts.items() }
		up["offset" ] = offset
		return url_for(url, "name").include_query_params(2**up)

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
		request=request, name="partials/nodeinfo.html", context={
			"title"        : title,
			"root"         : root,
			"target"       : target,

			"count_all"    : count_all,
			"count_filter" : count_filter,
			"count_res"    : count_res,

			"images"       : images,

			"data"         : tuple(r.model_pretty_dump() for r in resp),
			"query_filter" : query_filter,
			"html_filters" : html_filters,
			"url_self"     : url_self,
			"url_opts"     : url_opts,

			"calc_offset"  : calc_offset
		}
	)

