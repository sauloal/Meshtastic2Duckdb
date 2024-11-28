import math


from .. import db
from .. import models

from ._base import *

from bokeh.models   import PrintfTickFormatter, DatetimeTickFormatter
from bokeh.models   import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed    import components


QueryImageDimension  = Annotated[int   | None, Query(ge=100, le=10_000)]
QueryBarWidth        = Annotated[float | None, Query(ge=0.1, le=1.0   )]


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


