import asyncio
import logging
import discord
from discord.ext import commands
from discord import app_commands
from src import FzSocket


class FzCommands(commands.Cog):
    """Class for the Factorio Zone cog"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="test", description="test command")
    @app_commands.guilds(842947049489563700)
    async def test(self, ctx: discord.Interaction):
        await ctx.response.defer()
        fz_socket = FzSocket.FzSocket(ctx.user.name, "none")
        asyncio.create_task(fz_socket.connect())
        await ctx.followup.send("Connecting to FactorioZone...")
        visit_secret = await fz_socket.get_secret()
        await ctx.channel.send(f"Received visit secret: {visit_secret}")


async def setup(bot):
    await bot.add_cog(FzCommands(bot))
