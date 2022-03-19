import asyncio
import json
import logging
import discord
from discord.ext import commands
from discord import app_commands
from src import FzSocket


def _check_for_token(member: discord.Member):
    with open('fztokens.json', 'r') as f:
        data = json.load(f)
    if member.id in data["tokens"]:
        return data["tokens"][member.id]
    else:
        return None


class FzCommands(commands.Cog):
    """Class for the Factorio Zone cog"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="connect", description="Connect to Factorio Zone Servers")
    @app_commands.guilds(842947049489563700)
    async def _connect(self, ctx: discord.Interaction):
        await ctx.response.defer()
        # check if member has a token
        token = _check_for_token(ctx.user)
        if token is None:
            await ctx.followup.send("You need to register a token first")
        else:
            fz_socket = FzSocket.FzSocket(ctx.user, token)
            asyncio.create_task(fz_socket.connect())
            await ctx.followup.send("Connecting to FactorioZone...")
            visit_secret = await fz_socket.get_secret()
            await ctx.edit_original_message(content=f"Received visit secret: {visit_secret}")
            self.bot.active_sockets.append(fz_socket)

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
            with open('../fztokens.json', 'r+') as f:
                data = json.load(f)
                entry = {ctx.user.id: token}
                data["tokens"].append(entry)
                f.seek(0)
                f.write(json.dumps(data))
                f.truncate()
            await ctx.followup.send("Token registered")


async def setup(bot):
    await bot.add_cog(FzCommands(bot))
