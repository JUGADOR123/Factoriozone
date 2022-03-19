import asyncio
import json
import logging

import discord.member
import websockets

logger = logging.getLogger(__name__)
url = "wss://factorio.zone/ws"


class FzSocket:
    def __init__(self, owner: discord.member.Member, token: str):
        self.owner = owner

        self.connected = False
        self.logged_in = False
        self.visit_secret = None
        self.user_token = token
        self.regions = None
        self.saves = None
        self._event_received_secret = asyncio.Event()

    async def _handle_messages(self, websocket):
        async for message in websocket:
            await self._deconstruct_message(message)

    async def _deconstruct_message(self, message):
        message = json.loads(message)
        if "secret" in message:
            self.visit_secret = message["secret"]
            self._event_received_secret.set()
            logger.info("Visit secret: %s", self.visit_secret)
        else:
            logger.info(f"Message received: {message}")

    async def get_secret(self):
        await self._event_received_secret.wait()
        return self.visit_secret

    async def connect(self):
        async with websockets.connect(url) as websocket:
            self.connected = True
            await self._handle_messages(websocket)




