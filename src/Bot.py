import logging
import os
import sys
from datetime import datetime
from sys import gettrace

import discord
from discord.ext.commands import Bot
from prettytable import PrettyTable

from src.extras.database import start_db


class FzBot(Bot):
    def __init__(self):
        self.active_sockets = []
        super().__init__(command_prefix="==")
        if gettrace() is None:
            self.debug_guild = None
        else:
            self.debug_guild = discord.Object(id=842947049489563700)

    async def setup_hook(self) -> None:
        await start_db()
        logging.info("Database started")
        if gettrace():
            for file in os.listdir("src/devCogs/"):
                if file.endswith(".py") and not file.startswith("__"):
                    await self.load_extension(f"src.cogs.{file[:-3]}")
                    logging.info(f"Cog loaded: {file[:-3]} ")
        else:
            for file in os.listdir("src/cogs/"):
                if file.endswith(".py") and not file.startswith("__"):
                    await self.load_extension(f"src.cogs.{file[:-3]}")
                    logging.info(f"Cog loaded: {file[:-3]} ")

    async def on_ready(self):
        logging.info("Bot is ready")
        table = PrettyTable()
        table.field_names = ["Name", "Value"]
        table.add_row(["Bot Name", self.user.name])
        table.add_row(["Bot ID", self.user.id])
        table.add_row(["Discord Version", discord.__version__])
        table.add_row(["Python Version", "{}.{}.{}".format(*sys.version_info)])
        table.add_row(["Start Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        table.align["Name"] = "l"
        table.align["Value"] = "l"
        logging.info(f"\n{table}")
        await self.tree.sync(guild=self.debug_guild)
        logging.info("Command tree synced")
