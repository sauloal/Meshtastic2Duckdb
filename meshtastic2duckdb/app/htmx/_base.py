from ._router import *


@router.get("/")
async def mx_root(request: Request):
	title         = "Home"
	target        = "container"

	urls          = get_urls()
	root          = urls[title]

	return templates.TemplateResponse(
		request=request, name="index_index.html", context={
			"title"        : title,
			"target"       : target,

			"urls"         : urls,
			"root"         : root,
		}
	)

@router.get("/home")
async def mx_home(request: Request):
	title         = "Home"
	target        = "container"

	urls          = get_urls()
	root          = urls[title]

	return templates.TemplateResponse(
		request=request, name="index_home.html", context={
			"title"        : title,
			"target"       : target,

			"urls"         : urls,
			"root"         : root,
		}
	)

