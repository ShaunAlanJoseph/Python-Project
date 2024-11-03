from asyncio import run
from discord import Intents
from discord.ext import commands
from logging import info, getLogger, INFO

from config import DISCORD_API_TOKEN, ADMIN_CHANNEL_ID
from cogs.GeminiCog import GeminiAgent
from cogs.cf_cog import CFCog
from utils.context_manager import ContextManager


async def main():
    getLogger().setLevel(INFO)

    bot = commands.Bot(command_prefix="$", intents=Intents.all(),help_command=None)
    await bot.add_cog(CFCog(bot))
    await bot.add_cog(GeminiAgent(bot))

    ContextManager.setup_context_manager()

    @bot.event
    async def on_ready():  # type: ignore
        assert bot.user is not None
        info(f"Logged in as User: {bot.user.name} ID: {bot.user.id}")
        HQ = await bot.fetch_channel(ADMIN_CHANNEL_ID)
        await HQ.send(f"Logged in as User: {bot.user.name} ID: `{bot.user.id}`")  # type: ignore

        # Removing all Roles
        for guild in bot.guilds:
            async for user in guild.fetch_members():
                if user.bot:
                    continue
                await user.remove_roles(*user.roles[1:])
        await HQ.send("Removed all roles from all users.")  # type: ignore


    assert DISCORD_API_TOKEN is not None
    await bot.start(DISCORD_API_TOKEN)


if __name__ == "__main__":
    run(main())
