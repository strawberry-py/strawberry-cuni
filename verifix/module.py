from __future__ import annotations

import discord
from discord.ext import commands

from pie import logger

guild_log = logger.Guild.logger()
bot_log = logger.Bot.logger()

IMPORT_EX = None
try:
    from ...mgmt.verify.database import CustomMapping, MappingExtension, VerifyRule
except Exception as ex:
    IMPORT_EX = ex


class Verifix(commands.Cog, MappingExtension):
    name = "CUNI Verify"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if IMPORT_EX:
            bot_log.error(None, None, "Error during mgmt.verify database import:", exception=IMPORT_EX)
            return
        MappingExtension.register_extension(name=self.name, ext=self)
        bot_log.info(None, None, f"Registered {self.name} as CustomMapping handler.")

    def cog_unload(self):
        if IMPORT_EX:
            return

        MappingExtension.unregister_extension(name=self.name)
        bot_log.info(None, None, f"Unregistered {self.name} as CustomMapping handler.")

    async def _get_or_create_rule(self, guild_id: int, name: str) -> VerifyRule:
        rule = VerifyRule.get(guild_id=guild_id, name=name)

        if len(rule) != 0:
            return rule[0]

        bot_log.info(None, None, f"Creating rule {name} for guild {guild_id}.")

        return VerifyRule.add(guild_id=guild_id, name="cuni")

    async def map(self, guild_id: int, username: str = None, domain: str = None, email: str = None) -> CustomMapping | None:
        if domain.lower().endswith(".cuni.cz") or email.lower().endswith(".cuni.cz"):
            rule: VerifyRule = await self._get_or_create_rule(guild_id=guild_id, name="cuni")
            return rule

        return None
