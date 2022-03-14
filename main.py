import asyncio, logging, time, discord, coloredlogs
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dinteractions_Paginator import Paginator

import src.websocket as ws

if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )
    logger.info("Starting Client")
    loop= asyncio.get_event_loop()
    loop.run_until_complete(ws.receive("factorio.zone/ws"))
    loop.run_forever()


