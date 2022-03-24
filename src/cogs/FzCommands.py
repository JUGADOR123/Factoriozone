import json

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from src.extras.database import remove_token, append_token, get_all_data, get_tokens, FzToken


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
        # check if the user has any tokens

    @app_commands.command(name="server-list", description="List all Factorio Zone Active servers")
    @app_commands.guilds(842947049489563700)
    async def _server_list(self, ctx: discord.Interaction):
        await ctx.response.send_message(f"There are {len(self.bot.active_sockets)} active servers")

    @app_commands.command(name="my-tokens", description="Get all your tokens from FactorioZone")
    @app_commands.guilds(842947049489563700)
    async def _my_tokens(self, ctx: discord.Interaction):
        await ctx.response.defer()
        tokens: list[FzToken] = await get_tokens(ctx.user)
        if tokens:
            await ctx.followup.send(f"You currently have {len(tokens)} tokens")
            tokens_string = ""
            for token in tokens:
                tokens_string += f"{token.name} - {token.token_id}\n"
            await ctx.channel.send(f"```\n{tokens_string}```")
        else:
            await ctx.followup.send("You don't have any tokens")

    @app_commands.command(name="add-token", description="Register a token for FactorioZone")
    @app_commands.guilds(842947049489563700)
    async def _add_token(self, ctx: discord.Interaction, token: str, name: str = None):
        await ctx.response.defer()
        status = await append_token(ctx.user, token, name)
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
