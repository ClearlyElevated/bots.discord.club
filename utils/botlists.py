from aiohttp import ClientSession
import secrets
import json

from utils import restcord


class BotGrabber:
    def __init__(self, session = None, loop = None):
        self.session = session or ClientSession(loop=loop)
        self.bots = {}

    def _update_bots(self, bot_id, obj):
        bot_id = str(bot_id)
        if bot_id not in self.bots.keys():
            self.bots[bot_id] = {}

        for key, value in obj.items():
            if value is None or value == "":
                continue

            if isinstance(value, list):
                if not isinstance(self.bots[bot_id].get(key), list):
                    self.bots[bot_id][key] = []

                self.bots[bot_id][key] += value

            if isinstance(value, dict):
                if not isinstance(self.bots[bot_id].get(key), dict):
                    self.bots[bot_id][key] = {}

                self.bots[bot_id][key].update(value)

            else:
                self.bots[bot_id].update({key: value})

    async def _discordbots_org(self):
        url = "https://discordbots.org/api/bots?limit={limit}&offset={offset}&fields={fields}"
        fields = ["id", "username", "discriminator", "avatar", "prefix", "lib", "shortdesc", "tags", "owners", "invite", "date"]
        limit = 500
        offset = 0
        while True:
            async with self.session.get(url=url.format(limit=limit, offset=offset, fields=','.join(fields))) as resp:
                bots = await resp.json()
                if bots.get("results") is None or len(bots["results"]) == 0:
                    break

                for bot in bots["results"]:
                    self._update_bots(bot["id"], {
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
                                                      "https://discordbots.org/images/dblnew.png"]}
                    })

            offset += 500

    async def _bots_discord_pw(self):
        url = "https://bots.discord.pw/api/bots"
        async with self.session.get(url=url, headers={"Authorization": secrets.bots_discord_pw}) as resp:
            bots = await resp.json()
            for bot in bots:
                self._update_bots(bot["user_id"], {
                    "name": bot["name"],
                    "prefix": bot["prefix"],
                    "library": bot["library"],
                    "description": bot["description"],
                    "owners": bot["owner_ids"],
                    "invite": bot["invite_url"],
                    "lists": {"bots.discord.pw": [f"https://bots.discord.pw/bots/{bot['user_id']}",
                                                  "https://bots.discord.pw/images/default.jpg"]}
                })

    async def _botlist_space(self):
        url = "https://botlist.space/api/bots"
        async with self.session.get(url=url) as resp:
            bots = await resp.json()
            for bot in bots:
                if not bot["approved"]:
                    continue

                self._update_bots(bot["id"], {
                    "name": bot["username"],
                    "avatar_url": bot.get("avatar"),
                    "discriminator": bot["discriminator"],
                    "prefix": bot.get("prefix"),
                    "library": bot["library"],
                    "description": bot["short_description"],
                    "invite": bot["invite"],
                    "owners": [owner["id"] for owner in bot["owners"]],
                    "lists": {"botlist.space": [f"https://botlist.space/bot/{bot['id']}",
                                                "https://botlist.space/img/logo-transparent.png"]}
                })

    async def _discordbot_world(self):
        url = "https://discordbot.world/api/bots"
        async with self.session.get(url=url) as resp:
            bots = await resp.json()
            for bot in bots:
                self._update_bots(bot["id"], {
                    "name": bot["name"],
                    "discriminator": bot["tag"].split("#")[1],
                    "avatar_url": bot["avatar"],
                    "prefix": bot["prefix"],
                    "library": bot["library"],
                    "description": bot["short_description"],
                    "invite": bot["invite"],
                    "owners": [bot["owner"]["id"]] + (bot.get("other_owners") or []),
                    "lists": {"discordbot.world": [f"https://discordbot.world/bot/{bot['id']}",
                                                   "https://cdn.discordapp.com/icons/396440418507816960/aed0c9184d1e3abf28be02599b2c0f41.jpg"]}
                })

    async def update_bots(self):
        await self._discordbots_org()
        await self._bots_discord_pw()
        await self._botlist_space()
        await self._discordbot_world()
        await self._discordbot_world()

        print(len(self.bots))
