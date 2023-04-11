import os
import logging
import discord
from discord.ext import commands


extensions_list = ['user', 'info']

slippi_url_prefix = "https://slippi.gg/user/"

bot = commands.Bot(command_prefix=os.environ.get('DISCORD_COMMAND_PREFIX'), intents=discord.Intents.all())

logger = logging.getLogger(f'slippi_bot.{__name__}')


@bot.event
async def on_ready():

    for extension in extensions_list:
        try:
            await bot.load_extension(f'cogs.{extension}')
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            logger.error('Failed to load extension {}\n{}'.format(extension, exc))

    for cog in bot.cogs:
        logger.info(cog)

    # set bot status to online and game it is playing
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(
                                  type=discord.ActivityType.playing,
                                  name="Slippi"))
    logger.info('Logged in as: {0.user.name} | {0.user.id}'.format(bot))
