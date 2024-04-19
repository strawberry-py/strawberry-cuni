from __future__ import annotations

from discord.ext import commands, tasks

from pie import logger

guild_log = logger.Guild.logger()
bot_log = logger.Bot.logger()

IMPORT_EX = None
try:
    from ...mgmt.verify.database import CustomMapping, MappingExtension, VerifyRule
except Exception as ex:
    IMPORT_EX = ex


class Verifix(commands.Cog, MappingExtension):
    """This module works as extension for mgmt.verify module.

    If strawberry-py management repo is not installed, this module won't do anything.

    Otherwise it will register itself as CustomMapping handler.

    This handler users `cuni` VerifyRule. If it does not exists for the guild, it's automatically created.
    """

    name = "CUNI Verify"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.register.start()

    async def cog_unload(self):
        if IMPORT_EX:
            return

        MappingExtension.unregister_extension(name=self.name)
        await bot_log.info(
            None, None, f"Unregistered {self.name} as CustomMapping handler."
        )

        self.register.start()

    @tasks.loop(seconds=2.0, count=1)
    async def register(self):
        if IMPORT_EX:
            await bot_log.error(
                None, None, "Error during mgmt.verify database import:", exception=IMPORT_EX
            )
            return

        MappingExtension.register_extension(name=self.name, ext=self)
        await bot_log.info(None, None, f"Registered {self.name} as CustomMapping handler.")

    @register.before_loop
    async def before_register(self):
        """Ensures that bot is ready before registering
        """
        await self.bot.wait_until_ready()

    async def _get_or_create_rule(self, guild_id: int, name: str) -> VerifyRule:
        rule = VerifyRule.get(guild_id=guild_id, name=name)

        if len(rule) != 0:
            return rule[0]

        bot_log.info(None, None, f"Creating rule {name} for guild {guild_id}.")

        return VerifyRule.add(guild_id=guild_id, name="cuni")

    async def map(
        self, guild_id: int, username: str = None, domain: str = None, email: str = None
    ) -> CustomMapping | None:
        if (domain and domain.lower().endswith(".cuni.cz")) or (
            email and email.lower().endswith(".cuni.cz")
        ):
            rule: VerifyRule = await self._get_or_create_rule(
                guild_id=guild_id, name="cuni"
            )

            domain = domain if domain else email.split("@")[-1]

            mapping = CustomMapping(
                guild_id=guild_id,
                rule_id=rule.idx,
                username=None,
                domain=domain,
                rule=rule,
            )
            return mapping

        return None


async def setup(bot) -> None:
    await bot.add_cog(Verifix(bot))
