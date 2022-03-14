import asyncio, logging, time, discord, coloredlogs
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dinteractions_Paginator import Paginator

import src.websocket as ws

settings = json.load(open('settings.json'))
token = settings['token']

if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )
    logger.info("Starting Client")
    loop= asyncio.get_event_loop()
    loop.run_until_complete(ws.receive("factorio.zone/ws"))
    loop.run_forever()

class Bot(commands.AutoShardedBot):
    """Subclassing Bot because we do some different things here"""
    @property
    def utils(self):
        """Define the default utilities"""
        return utils

    @property
    def web(self):
        """Makes aiohttp a global session"""
        return utils.WebHelper.session

    @property
    def db(self):
        """Makes Redis a global session"""
        return utils.DatabaseHandler.db

    async def on_ready(self):
        # Remove help because it's done with commands
        
        # Set status
        await self.change_presence(activity=nextcord.Game(name="API for factorio.zone"))
        """for file in os.listdir('modules/events'):
            # Load invisible cogs
            direc = 'modules.events.'
            if not file.startswith('__'):
                name = file.replace('.py','')
                self.load_extension(direc + name)"""
        for x in os.walk('modules/commands', topdown=False):
            # Load command cogs
            for y in x[1]:
                if not y.startswith('__'):
                    direc = 'modules.commands.{}.'.format(y)
                    for file in os.listdir('modules/commands/{}'.format(y)):
                        if not file.startswith('__'):
                            name = file.replace('.py','')
                            self.load_extension(direc + name)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        print('All cogs loaded')
        print('------')
        print('Statistics')
        print(str(len(self.guilds)) + ' - ' + str(self.shard_count) + ' (Guilds/Shards)')
        print('------')
        print('Initialization Complete')

bot = Bot(command_prefix="!")
bot.remove_command('help')