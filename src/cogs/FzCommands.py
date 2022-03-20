import asyncio
import json
import logging
import discord
from discord.ext import commands
from discord import app_commands
from src import FzSocket
import aiohttp


def _check_for_token(member: discord.Member):
    pass


class FzCommands(commands.Cog):
    """Class for the Factorio Zone cog"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def _fz_login(self, visit_token: str, private_token: str):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://factorio.zone/api/user/login",
                                    data={"userToken": private_token, "visitSecret": visit_token, "reconnected": False,
                                          "script": "https://factorio.zone/cache/main.355cce551d992ff91c29.js"}) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None

    @app_commands.command(name="connect", description="Connect to Factorio Zone Servers")
    @app_commands.guilds(842947049489563700)
    async def _connect(self, ctx: discord.Interaction):
        await ctx.response.defer()
        # check if member has a token
        # token = _check_for_token(ctx.user)
        fz_socket = FzSocket.FzSocket(ctx.user)
        asyncio.create_task(fz_socket.connect())
        await ctx.followup.send("Connecting to FactorioZone...")
        visit_secret = await fz_socket.get_secret()
        await ctx.edit_original_message(content=f"Received visit secret: {visit_secret}")
        self.bot.active_sockets.append(fz_socket)
        resp = await self._fz_login(visit_secret, "SxIPKrHPEKNqKkDiyOKAHOic")
        if resp is not None:
            await ctx.channel.send("Successfully logged in to FactorioZone!")
            await asyncio.sleep(2)
            regions = await fz_socket.get_regions()
            await ctx.channel.send(f"Regions: ``` \n{regions}```")
            await asyncio.sleep(1)
            saves = await fz_socket.get_saves()
            await ctx.channel.send(f"Saves: ``` \n{saves}```")
            await asyncio.sleep(1)
            versions = await fz_socket.get_versions()
            await ctx.channel.send(f"Versions: ``` \n{versions}```")

    @app_commands.command(name="server-list", description="List all Factorio Zone Active servers")
    @app_commands.guilds(842947049489563700)
    async def _server_list(self, ctx: discord.Interaction):
        await ctx.response.send_message(f"There are {len(self.bot.active_sockets)} active servers")

    @app_commands.command(name="register", description="Register a token for FactorioZone")
    @app_commands.guilds(842947049489563700)
    async def _register(self, ctx: discord.Interaction, token: str):
        await ctx.response.defer()
        # check if the member already has a token
        if _check_for_token(ctx.user) is not None:
            await ctx.followup.send("You already have a token registered")
        else:

            await ctx.followup.send("Token registered")


async def setup(bot):
    await bot.add_cog(FzCommands(bot))
