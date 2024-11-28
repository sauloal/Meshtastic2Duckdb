import datetime

from fastapi                        import FastAPI, APIRouter, Request, Response, Path, Query, Depends
from fastapi                        import status

from fastapi.templating             import Jinja2Templates
from fastapi.responses              import HTMLResponse

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


def get_urls():
        return {
                "Home"     : "mx_home",
                "Node Info": "mx_messages_nodeinfo"
        }
