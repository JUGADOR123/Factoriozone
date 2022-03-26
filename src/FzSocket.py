import asyncio
import json
import logging

import discord.member
import websockets

logger = logging.getLogger(__name__)
url = "wss://factorio.zone/ws"


class FzSocket:
    def __init__(self, owner: discord.member.Member):
        self.owner = owner

        self.logged_in = False
        self.visit_secret = None
        self.regions = None
        self.saves = None
        self.versions = None
        self._connected_event = asyncio.Event()
        self._event_received_secret = asyncio.Event()
        self._event_received_regions = asyncio.Event()
        self._event_received_saves = asyncio.Event()
        self._event_received_versions = asyncio.Event()
        self._event_received_mods = asyncio.Event()

    async def _handle_messages(self, websocket):
        async for message in websocket:
            await self._deconstruct_message(message)

    async def _deconstruct_message(self, message):
        message = json.loads(message)
        if "secret" in message:
            self.visit_secret = message["secret"]
            self._event_received_secret.set()

        elif 'name' in message and message['name'] == 'regions':
            self.regions = message["options"]
            self._event_received_regions.set()
        elif "name" in message and message["name"] == "versions":
            self.versions = message["options"]
            self._event_received_versions.set()
        elif "name" in message and message["name"] == "saves":
            self.saves = message["options"]
            self._event_received_saves.set()
        else:
            logger.info(f"Message received: {message}")

    async def get_secret(self):
        await self._event_received_secret.wait()
        return self.visit_secret

    async def get_regions(self):
        await self._event_received_regions.wait()
        return self.regions

    async def get_saves(self):
        await self._event_received_saves.wait()
        return self.saves

    async def get_versions(self):
        await self._event_received_versions.wait()
        return self.versions

    async def connect(self):
        async with websockets.connect(url) as websocket:
            self._connected_event.set()
            await self._handle_messages(websocket)
