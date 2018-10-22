from aiohttp import web, ClientSession
import aiohttp_jinja2, jinja2

import secrets
from sites import index
from utils import database


startup_sites = [index]


async def prepare(app):
    app["http_session"] = ClientSession()
    app.secrets = secrets

    for site in startup_sites:
        await site.setup(app)

    await database.setup(app["http_session"])


app = web.Application()
app.on_startup.append(prepare)
app.router.add_static('/static', "./static")
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./contents/templates"))
web.run_app(app, port=8081)
