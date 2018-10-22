from aiohttp import web
import aiohttp_jinja2 as jinja2

from utils import database


routes = web.RouteTableDef()

@routes.get("/new")
async def search(request):
    bots = await database.get_bots()
    return jinja2.render_template("/index.html", request,
                                  {"bots": {key: value for key, value in list(bots.items())[:10]}})

@routes.get("/search")
async def search(request):
    search = request.query.get("s")
    bots = await database.get_bots()
    return jinja2.render_template("/index.html", request,
                                  {"bots": {key: value for key, value in list(bots.items())[:10]},
                                   "search": search})

@routes.get("/top")
async def search(request):
    bots = await database.get_bots()
    return jinja2.render_template("/index.html", request,
                                  {"bots": {key: value for key, value in list(bots.items())[:10]}})


@routes.get("/")
async def index(request):
    bots = await database.get_bots()
    return jinja2.render_template("/index.html", request,
                                  {"bots": {key: value for key, value in list(bots.items())[:10]}})


async def setup(app):
    app.add_routes(routes)