from fastapi            import FastAPI, APIRouter, status, Request, Response, Path, Query
from fastapi            import Depends

from fastapi.templating import Jinja2Templates
from fastapi.responses  import HTMLResponse

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

# https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates
#
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-bar-charts/
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-line-charts/
# https://github.com/bugbytes-io/django-htmx-bokeh/tree/barchart
# https://github.com/ocramz/htmx-plotly
# https://htmx.org/examples/lazy-load/

router = APIRouter(tags=["HTMX"], include_in_schema=False)

templates = Jinja2Templates(directory="templates")

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
        "Home": "mx_start",
        "Temp": "mx_charts_temp"
    }

QueryYear  = Annotated[int | None, AfterValidator(validate_year),  Query(default_factory=year_get_max)]
QueryCount = Annotated[int | None, Query(ge=5, le=1_000)]


@router.get("/", response_class=HTMLResponse)
async def mx_root(request: Request, year: QueryYear, count: QueryCount = 10):
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

@router.get("/start", response_class=HTMLResponse)
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





from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components

QueryImageDimension  = Annotated[int   | None, Query(ge=100, le=10_000)]
QueryBarWidth        = Annotated[float | None, Query(ge=0.1, le=1.0   )]


@router.get("/charts/temp", response_class=HTMLResponse)
async def mx_charts_temp(request: Request, year: QueryYear, count: QueryCount = 10, image_width: QueryImageDimension = 500, image_height: QueryImageDimension = 500, bar_width: QueryBarWidth=0.8):
    urls          = get_urls()
    title         = "Temp"
    root          = urls[title]

    column_labels = list( str(v) for v in range(1, count+1) )
    column_values = list(                 range(1, count+1))

    cds           = ColumnDataSource(data=dict(column_labels=column_labels, column_values=column_values))
    fig           = figure(x_range=column_labels, height=image_height, width=image_width, title=f"Top {count} Values for year ({year})")
    fig.vbar(x='column_labels', top='column_values', width=bar_width, source=cds)
    script, div   = components(fig)

    years         = list( range(year_get_min(), year_get_max()+1) )

    return templates.TemplateResponse(
        request=request, name="partials/graphs.html", context={
            "title"        : title,
            "root"         : root,

            "years"        : years,
            "year_selected": year,
            "count"        : count,

            "script"       : script,
            "div"          : div,
	}
    )

