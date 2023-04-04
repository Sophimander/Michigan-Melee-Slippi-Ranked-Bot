from slippi import slippi_ranked, slippi_data
from database import database_setup
from database import database_operations as do
import discord_bot
import logging
import sys
import os

logger = logging.getLogger('slippi_bot')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log.log')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)
formatter = logging.Formatter('%(asctime)s : %(module)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def main():
    logger.debug('Main ran')

    # Get environment variables
    discord_token = os.environ.get('DISCORD_TOKEN')
    slippi_username = os.environ.get('SLIPPI_USERNAME')
    slippi_password = os.environ.get('SLIPPI_PASSWORD')

    slippi_ranked.username = slippi_username
    slippi_ranked.password = slippi_password

    # Create database
    with do.create_con('database.db') as conn:
        database_setup.create_database(conn, conn.cursor())

    # Start bot
    discord_bot.bot.run(discord_token)


if __name__ == '__main__':
    main()

