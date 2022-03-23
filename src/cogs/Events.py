import logging

import discord
from discord.ext import commands


class Events(commands.Cog):
    """Class for the Events cog"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logging.error(f"An error occurred while handling {event}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author is not self.bot:
            logging.info(f"Message Received on {message.guild}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author is not self.bot:
            logging.info(f"Message Deleted on {message.guild}")


async def setup(bot):
    await bot.add_cog(Events(bot))
