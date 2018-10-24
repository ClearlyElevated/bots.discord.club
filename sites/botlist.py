import asyncio

import aiohttp_jinja2 as jinja2
from aiohttp import web

from utils import database as db, grabber

routes = web.RouteTableDef()
per_page = 12


@routes.get("/about")
async def about(request):
    return jinja2.render_template("/about.html", request, {})


@routes.get("/new")
async def search(request):
    try:
        page = int(request.query.get("page"))
    except:
        page = 1

    cursor = await db.rdb.table('bots').order_by(index=db.rdb.desc('timestamp')).skip((page - 1) * per_page).limit(
        per_page).run(db.con)
    bots = await db.cursor_to_list(cursor)
    return jinja2.render_template("/new.html", request, {"bots": bots, "page": page})


@routes.get("/search")
async def search(request):
    try:
        page = int(request.query.get("page"))
    except:
        page = 1

    search = str(request.query.get("s")).lower()
    cursor = await db.rdb.table("bots").filter(
        lambda b: b["description"].downcase().match(search) | b["name"].downcase().match(search)).skip(
        (page - 1) * per_page).limit(per_page).run(db.con)
    bots = await db.cursor_to_list(cursor)
    return jinja2.render_template("/search.html", request,
                                  {"bots": bots, "search": search, "page": page})


@routes.get("/")
async def index(request):
    per_page = 6
    try:
        page = int(request.query.get("page"))
    except:
        page = 1

    featured_bots = await db.rdb.table("bots").sample(per_page).run(db.con)
    new_cursor = await db.rdb.table('bots').order_by(index=db.rdb.desc('timestamp')).skip((page - 1) * per_page).limit(
        per_page).run(db.con)
    return jinja2.render_template("/index.html", request, {"featured_bots": featured_bots,
                                                           "new_bots": await db.cursor_to_list(new_cursor),
                                                           "page": page})


async def update_bots(app):
    while True:
        print("Updating bots ...")
        await grabber.update_bots(app["http_session"])
        print("Finished updating")
        await asyncio.sleep(15 * 60)


async def setup(app):
    app.add_routes(routes)
    app.loop.create_task(update_bots(app))
