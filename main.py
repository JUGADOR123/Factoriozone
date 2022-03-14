import asyncio
import logging
import time

import coloredlogs
import src.websocket as ws

if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )
    logger.info("Starting Client")
    loop= asyncio.get_event_loop()
    loop.run_until_complete(ws.receive("factorio.zone/ws"))
    loop.run_forever()


