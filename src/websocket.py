import asyncio
import json
import logging

import aiohttp
import websockets


async def receive_handle(websocket: str):
    async for message in websocket:
        await handle_message(message)


async def receive(websocket: str):
    async with websockets.connect(f"wss://{websocket}") as websocket:
        await receive_handle(websocket)


async def handle_message(message: str):
    message = json.loads(message)
    if "secret" in message:
        logging.info(f"Client Secret Received: {message['secret']}")
        #await login("SxIPKrHPEKNqKkDiyOKAHOic", message['secret'])
    else:
        logging.info(f"Client Message Received: {message}")


async def login(user_token: str, Session_secret: str):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://factorio.zone/api/user/login",  data={"userToken": user_token, "visitSecret": Session_secret,"reconnected":False,"script":"https://factorio.zone/cache/main.355cce551d992ff91c29.js"}) as response:
            response = await response.json()
            logging.info(f"Login Response: {response}")
