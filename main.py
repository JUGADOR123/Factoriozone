import asyncio, logging, time, coloredlogs, json, discord
from discord.ext import commands
import interactions

import src.websocket as ws

settings = json.load(open('settings.json'))
token = settings['token']
logger = logging.getLogger()
coloredlogs.install(level='DEBUG', logger=logger, fmt=f"[%(module)-1s]|[%(levelname)-1s]| %(message)s", )


"""if __name__ == "__main__":
    logger.info("Starting Client")
    loop= asyncio.get_event_loop()
    loop.run_until_complete(ws.receive("factorio.zone/ws"))
    loop.run_forever()"""

class Bot(commands.AutoShardedBot):
    """Subclassing Bot because we do some different things here"""

    async def on_ready(self):
        # Remove help because it's done with commands
        
        # Set status
        await self.change_presence(activity=discord.Game(name="API for factorio.zone"))
        """for file in os.listdir('modules/events'):
            # Load invisible cogs
            direc = 'modules.events.'
            if not file.startswith('__'):
                name = file.replace('.py','')
                self.load_extension(direc + name)"""
        """for x in os.walk('modules/commands', topdown=False):
            # Load command cogs
            for y in x[1]:
                if not y.startswith('__'):
                    direc = 'modules.commands.{}.'.format(y)
                    for file in os.listdir('modules/commands/{}'.format(y)):
                        if not file.startswith('__'):
                            name = file.replace('.py','')
                            self.load_extension(direc + name)"""
        logging.info('Logged in as')
        logging.info(self.user.name)
        logging.info(self.user.id)
        logging.info('------')
        logging.info('All cogs loaded')
        logging.info('------')
        logging.info('Statistics')
        logging.info(str(len(self.guilds)) + ' - ' + str(self.shard_count) + ' (Guilds/Shards)')
        logging.info('------')
        logging.info('Initialization Complete')

bot = Bot(command_prefix="/")
bot.remove_command('help')
slash = interactions.SlashCommand(bot, sync_commands=True)

@slash.slash(
    name="help",
    description="Gets the commands for the bot",
    guild_ids=[926227211659386981]
)
async def help(ctx: SlashContext):
    login = discord.Embed(title="/login", description="This makes the bot login to factorio.zone", color=discord.Color.red())
    start = discord.Embed(title="/start", description="This allows you to start your server", color=discord.Color.orange())
    stop = discord.Embed(title="/stop", description="This allows you to stop your server", color=discord.Color.gold())
    four = discord.Embed(title="4th Embed", description="General Kenobi!", color=discord.Color.green())
    five = discord.Embed(title="5th Embed", description="General Kenobi!", color=discord.Color.blue())
    pages = [login, start, stop, four, five]

    await Paginator(bot=bot, ctx=ctx, pages=pages, timeout=60).run()

@slash.slash(
    name="setusertoken",
    description="Sets the user token for your server",
    guild_ids=[926227211659386981],
    options=[
        create_option(
            name="usertoken",
            description="Put your user token from factorio.zone here",
        required=True,
        option_type=3
        )
    ]
)
async def settings(ctx:SlashContext, usertoken:str):
    await ctx.send(usertoken)

bot.run(token)