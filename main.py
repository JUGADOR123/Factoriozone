import json

import coloredlogs
import logging
from dotenv import load_dotenv
from sys import gettrace
import os
from src.Bot import FzBot


def setup():
    logger = logging.getLogger()
    load_dotenv("token.env")

    if not os.path.isfile("fztokens.json"):
        with open("fztokens.json", "w") as f:
            data = {"tokens": []}
            json.dump(data, f, indent=4)
        logger.error("Token file not found, creating one")

    if gettrace() is None:
        coloredlogs.install(level='INFO', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )

        token = os.getenv("release_token")
        logger.info("Logging in as User...")
        bot = FzBot()

        bot.run(token)
    else:
        coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )
        logger.info("Running in Debug Mode...")
        token = os.getenv("debug_token")
        bot = FzBot()

        bot.run(token)


if __name__ == "__main__":
    setup()
