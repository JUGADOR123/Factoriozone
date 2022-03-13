import asyncio
import logging
import time

import coloredlogs
import src.websocket as ws

if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )
    logger.info("Starting Client")
    socket = ws.WebSocket()
    asyncio.run(socket.start())
    time.sleep(10)
    socket.stop()
