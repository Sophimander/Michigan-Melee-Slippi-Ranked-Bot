from slippi import slippi_ranked, slippi_data
from database import database_setup
from database import database_operations as do
import discord_bot
import logging
import sys
import os


logger = logging.getLogger('slippi_bot')
logger.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('log.log')

stdout_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)


def main():
    logger.debug('Main ran')

    # Get environment variables
    discord_token = os.environ.get('DISCORD_TOKEN')

    # Create database
    with do.create_con('database.db') as conn:
        database_setup.create_database(conn, conn.cursor())

    # Start bot
    discord_bot.bot.run(discord_token)


if __name__ == '__main__':
    main()

