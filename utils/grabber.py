from aiohttp import ClientSession
import secrets
from datetime import datetime
import time

from utils import restcord, database as db


async def _update_bots(bot_id, obj):
    res = {}
    for key, value in obj.items():
        if value is not None and value != "":
            res[key] = value

    obj = res

    table = db.rdb.table("bots")
    if await table.get(bot_id).run(db.con) is None:
        await table.insert({"id": bot_id, "timestamp": time.mktime(datetime.utcnow().timetuple()), **obj}).run(db.con)

    else:
        await table.get(bot_id).update(obj).run(db.con)


async def _discordbots_org(session):
    url = "https://discordbots.org/api/bots?limit={limit}&offset={offset}&fields={fields}"
    fields = ["id", "username", "discriminator", "avatar", "prefix", "lib", "shortdesc", "tags", "owners", "invite",
              "date"]
    limit = 500
    offset = 0
    while True:
        async with session.get(url=url.format(limit=limit, offset=offset, fields=','.join(fields))) as resp:
            bots = await resp.json()
            if bots.get("results") is None or len(bots["results"]) == 0:
                break

            for bot in bots["results"]:
                await _update_bots(bot["id"], {
                    "name": bot["username"],
                    "avatar_url": restcord.get_avatar_url(bot.get("avatar"), bot["id"], bot["discriminator"]),
                    "discriminator": bot["discriminator"],
                    "prefix": bot["prefix"],
                    "library": bot["lib"],
                    "description": bot["shortdesc"],
                    "tags": bot["tags"],
                    "owners": bot["owners"],
                    "invite": bot["invite"],
                    "lists": {"discordbots.org": [f"https://discordbots.org/bot/{bot['id']}",
                                                  "https://discordbots.org/favicon.ico"]}
                })

        offset += 500


async def _bots_discord_pw(session):
    url = "https://bots.discord.pw/api/bots"
    async with session.get(url=url, headers={"Authorization": secrets.bots_discord_pw}) as resp:
        bots = await resp.json()
        for bot in bots:
            await _update_bots(bot["user_id"], {
                "name": bot["name"],
                "prefix": bot["prefix"],
                "library": bot["library"],
                "description": bot["description"],
                "owners": bot["owner_ids"],
                "invite": bot["invite_url"],
                "lists": {"bots.discord.pw": [f"https://bots.discord.pw/bots/{bot['user_id']}",
                                              "https://bots.discord.pw/favicon.ico"]}
            })


async def _botlist_space(session):
    url = "https://botlist.space/api/bots"
    async with session.get(url=url) as resp:
        bots = await resp.json()
        for bot in bots:
            if not bot["approved"]:
                continue

            await _update_bots(bot["id"], {
                "name": bot["username"],
                "avatar_url": bot.get("avatar"),
                "discriminator": bot["discriminator"],
                "prefix": bot.get("prefix"),
                "library": bot["library"],
                "description": bot["short_description"],
                "invite": bot["invite"],
                "owners": [owner["id"] for owner in bot["owners"]],
                "lists": {"botlist.space": [f"https://botlist.space/bot/{bot['id']}",
                                            "https://botlist.space/favicon.ico"]}
            })


async def _discordbot_world(session):
    url = "https://discordbot.world/api/bots"
    async with session.get(url=url) as resp:
        bots = await resp.json()
        for bot in bots:
            await _update_bots(bot["id"], {
                "name": bot["name"],
                "discriminator": bot["tag"].split("#")[1],
                "avatar_url": bot["avatar"],
                "prefix": bot["prefix"],
                "library": bot["library"],
                "description": bot["short_description"],
                "invite": bot["invite"],
                "owners": [bot["owner"]["id"]] + (bot.get("other_owners") or []),
                "lists": {"discordbot.world": [f"https://discordbot.world/bot/{bot['id']}",
                                               "https://discordbot.world/icons/favicon.ico"]}
            })


async def _bots_discordlist_app(session):
    url = "https://bots.discordlist.app/api/bots"
    async with session.get(url=url) as resp:
        bots = await resp.json()
        for bot in bots:
            await _update_bots(bot["_id"], {
                "name": bot["username"],
                "discriminator": bot["discriminator"],
                "avatar_url": restcord.get_avatar_url(bot.get("avatar"), bot["_id"], bot["discriminator"]),
                "prefix": bot["prefix"],
                "library": bot["library"],
                "description": bot["shortdesc"],
                "invite": bot["invite"],
                "owners": [bot["owner"]] + (bot.get("otherowners") or []),
                "lists": {"bots.discordlist.app": [f"https://bots.discordlist.app/bot/{bot['_id']}",
                                                   "https://bots.discordlist.app/static/favicon.ico"]}
            })


async def update_bots(session):
    await _discordbots_org(session)
    await _bots_discord_pw(session)
    await _botlist_space(session)
    await _discordbot_world(session)
    await _discordbot_world(session)
    await _bots_discordlist_app(session)
