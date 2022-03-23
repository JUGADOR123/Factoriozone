import asyncio
import json

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from src import FzSocket
from src.extras.database import remove_token, append_token, get_all_data


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
            saves = await fz_socket.get_saves()
            versions = await fz_socket.get_versions()
            await ctx.channel.send(
                f"Regions: ```{regions}``` \n Saves: \n ```{saves}``` \n Versions:\n ```{versions}```")

    @app_commands.command(name="server-list", description="List all Factorio Zone Active servers")
    @app_commands.guilds(842947049489563700)
    async def _server_list(self, ctx: discord.Interaction):
        await ctx.response.send_message(f"There are {len(self.bot.active_sockets)} active servers")

    @app_commands.command(name="add-token", description="Register a token for FactorioZone")
    @app_commands.guilds(842947049489563700)
    async def _register(self, ctx: discord.Interaction, token: str):
        await ctx.response.defer()
        status = await append_token(ctx.user, token)
        if status:
            await ctx.followup.send("Successfully added token")
        else:
            await ctx.followup.send("You already have that token")

    @app_commands.command(name="remove-token", description="Remove a token from FactorioZone")
    @app_commands.guilds(842947049489563700)
    async def _remove(self, ctx: discord.Interaction, token: str):
        await ctx.response.defer()
        status = await remove_token(ctx.user, token)
        if status:
            await ctx.followup.send("Successfully removed token")
        else:
            await ctx.followup.send("You don't have that token")

    @app_commands.command(name="get-all-data", description="Get all data from FactorioZone")
    @app_commands.guilds(842947049489563700)
    async def _get_all_data(self, ctx: discord.Interaction):
        await ctx.response.defer()
        data = await get_all_data()
        data = json.dumps(data, indent=4)
        await ctx.followup.send(f"```\n{data}```")


async def setup(bot):
    await bot.add_cog(FzCommands(bot))