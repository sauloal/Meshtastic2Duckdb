from fastapi             import FastAPI, APIRouter, status, Request, Response, Path, Query

from fastapi.templating import Jinja2Templates
from fastapi.responses  import HTMLResponse

# https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates
#
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-bar-charts/
# https://www.bugbytes.io/posts/django-bokeh-and-htmx-data-driven-line-charts/
# https://github.com/bugbytes-io/django-htmx-bokeh/tree/barchart
# https://github.com/ocramz/htmx-plotly
# https://htmx.org/examples/lazy-load/

router = APIRouter(tags=["HTMX"], include_in_schema=False)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def mx_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@router.get("/test", response_class=HTMLResponse)
async def mx_test(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

