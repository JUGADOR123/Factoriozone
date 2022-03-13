import asyncio
import json
import logging

import websockets


class WebSocket:
    def __init__(self):
        self.uri = "wss://factorio.zone/ws"
        self.active: bool = False

    async def __connect(self):
        async with websockets.connect(self.uri) as websocket:
            async for message in websocket:

                message = json.loads(message)
                if message['secret']:
                    logging.info(f"Session ID Received: {message['secret']}")

    async def start(self):
        logging.info("Starting websocket")
        self.active = True
        await self.__connect()

    async def stop(self):
        logging.info("Stopping websocket")
        self.active = False
        # await self.__connect()
