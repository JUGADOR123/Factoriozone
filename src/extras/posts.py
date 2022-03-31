import aiohttp


async def fz_login_post(visit_token: str, private_token: str):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://factorio.zone/api/user/login",
                                data={"userToken": private_token, "visitSecret": visit_token, "reconnected": False,
                                      "script": "https://factorio.zone/cache/main.355cce551d992ff91c29.js"}) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None


async def fz_start_post(visit_token: str, region: str, version: str, save: str):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://factorio.zone/api/instance/start",
                                data={"visitSecret": visit_token, "region": region, "version": version,
                                      "save": save}) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None


async def fz_stop_post(visit_secret: str, launch_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://factorio.zone/api/instance/stop",
                                data={"visitSecret": visit_secret, "launchId": f"{launch_id}"}) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None

async def fz_command_post(visit_secret: str, launch_id: str, command:str):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://factorio.zone/api/instance/console",
                                data={"visitSecret": visit_secret, "launchId": f"{launch_id}", "input": command}) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None