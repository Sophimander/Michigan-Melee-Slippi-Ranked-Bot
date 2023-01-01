import os
import selenium.common.exceptions
import re
import discord
from discord.ext import commands

import math
import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import slippi.slippi_ranked as sr
import slippi.slippi_data as sd
import database.database_operations as do

'''
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
'''

extensions_list = ['user', 'info']

slippi_url_prefix = "https://slippi.gg/user/"

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())


@bot.event
async def on_ready():
    sr.login()

    for extension in extensions_list:
        try:
            await bot.load_extension(f'cogs.{extension}')
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    for cog in bot.cogs:
        print(cog)

    # set bot status to online and game it is playing
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(
                                  type=discord.ActivityType.playing,
                                  name="Slippi"))
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))
