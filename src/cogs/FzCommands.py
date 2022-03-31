import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from src.extras.FzSocket import FzSocket
from src.extras.database import remove_token, append_token, get_tokens, FzToken
from src.extras.posts import fz_login_post, fz_start_post, fz_stop_post, fz_command_post
from src.extras.settingsSelector import SettingsSelectorView
from src.extras.tokenSelector import TokenSelectorView


class FzCommands(commands.Cog):
    """Class for the Factorio Zone cog"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="console", description="Send a command to factorio.zone console")
    async def _console(self, ctx:discord.Interaction, command: str):
        await ctx.response.defer(ephemeral=True)
        for user_id, socket, socket_task in self.bot.active_sockets:
            if user_id == ctx.user.id:
                await ctx.edit_original_message(content="Sending console command: "+ command, view=None)
                response = await fz_command_post(socket.visit_secret, socket.launch_id, command)
                if response is not None:
                    await ctx.edit_original_message(content="Console command successfully sent", view=None)
                else:
                    await ctx.edit_original_message(content="Console command not sent", view=None)
                    status = True
        if not status:
            await ctx.edit_original_message(content="You don't have a server running", view=None)
    
    @app_commands.command(name="connect", description="Connect to Factorio Zone Servers")
    async def _connect(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        # check if the user has any tokens
        tokens = await get_tokens(ctx.user)
        if not tokens:
            await ctx.edit_original_message(content="You don't have any tokens, please user /add-token to add one")
        else:
            # if the user is on the list of active sockets, then we don't need to do anything
            for user_id, socket, socket_task in self.bot.active_sockets:
                if user_id == ctx.user.id:
                    await ctx.edit_original_message(content="You are already connected to a server", view=None)
                    return
            dropdown = TokenSelectorView(tokens)
            await ctx.edit_original_message(content=f"Select a token to connect to:", view=dropdown)
            await dropdown.wait()
            socket = FzSocket(ctx.user.id)
            socket_task = asyncio.create_task(socket.connect())
            respo = await fz_login_post(await socket.get_secret(), dropdown.token)
            if respo is not None:
                regions = await socket.get_regions()
                saves = await socket.get_saves()
                versions = await socket.get_versions()
                settingsView = SettingsSelectorView(regions, saves, versions)
                await ctx.edit_original_message(content=f"Select the settings", view=settingsView)
                await settingsView.wait()
                await ctx.edit_original_message(content=f"Starting the server", view=None)
                response = await fz_start_post(socket.visit_secret, settingsView.selected_region,
                                               settingsView.selected_version, settingsView.selected_save)
                if response is not None:
                    ip = await socket.get_ip()
                    launchId = await socket.get_launch_id()
                    await ctx.edit_original_message(content=f"Server started at `{ip}`\nLaunch Id: {launchId}",
                                                    view=None)
                    self.bot.active_sockets.append((ctx.user.id, socket, socket_task))

    @app_commands.command(name="stop", description="Stop the FactorioZone server")
    async def _stop(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        status = False
        for user_id, socket, socket_task in self.bot.active_sockets:
            if user_id == ctx.user.id:
                await ctx.edit_original_message(content="Stopping the server", view=None)
                response = await fz_stop_post(socket.visit_secret, socket.launch_id)
                if response is not None:
                    await ctx.edit_original_message(content="Server stopped", view=None)
                    self.bot.active_sockets.remove((user_id, socket, socket_task))
                    socket_task.cancel()
                    status = True
                    break
                else:
                    await ctx.edit_original_message(content="Server not stopped", view=None)
                    status = True
                break
        if not status:
            await ctx.edit_original_message(content="You don't have a server running", view=None)

    @app_commands.command(name="server-list", description="List all Factorio Zone Active servers")
    async def _server_list(self, ctx: discord.Interaction):
        await ctx.response.send_message(f"There are {len(self.bot.active_sockets)} active servers")

    @app_commands.command(name="my-tokens", description="Get all your tokens from FactorioZone")
    async def _my_tokens(self, ctx: discord.Interaction):
        await ctx.response.defer(ephemeral=True)
        tokens: list[FzToken] = await get_tokens(ctx.user)
        if tokens:
            tokens_string = ""
            for token in tokens:
                tokens_string += f"{token.name} - {token.token_id}\n"
            await ctx.edit_original_message(
                content=f"You currently have {len(tokens)} Tokens: \n```json\n{tokens_string}```")
        else:
            await ctx.edit_original_message(content="You don't have any tokens")

    @app_commands.command(name="add-token", description="Register a token for FactorioZone")
    async def _add_token(self, ctx: discord.Interaction, token: str, name: str = None):
        await ctx.response.defer(ephemeral=True)
        status = await append_token(ctx.user, token, name)
        if status:
            await ctx.edit_original_message(content="Successfully added token")
        else:
            await ctx.edit_original_message(content="You already have that token")

    @app_commands.command(name="remove-token", description="Remove a token from FactorioZone")
    async def _remove(self, ctx: discord.Interaction, token: str):
        await ctx.response.defer(ephemeral=True)
        status = await remove_token(ctx.user, token)
        if status:
            await ctx.edit_original_message(content="Successfully removed token")
        else:
            await ctx.edit_original_message(content="You don't have that token")


async def setup(bot):
    await bot.add_cog(FzCommands(bot))
