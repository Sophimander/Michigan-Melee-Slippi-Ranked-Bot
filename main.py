from slippi import slippi_ranked, slippi_data
from database import database_setup
from database import database_operations as do
import discord_bot
import logging
import sys
import configparser
from os.path import exists

logger = logging.getLogger('slippi_bot')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log.log')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)
formatter = logging.Formatter('%(asctime)s : %(module)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

config_path = 'ranked.ini'
config = configparser.ConfigParser()
config.read(config_path)


def first_run():
    logger.debug('First_run')
    slippi_username = input('Please input slippi.gg username ')
    slippi_password = input('Please input slippi.gg password ')
    discord_token = input('Please input discord bot token ')
    database_path = input('Please input the full database path ')
    config['DEFAULT']['Username'] = slippi_username
    config['DEFAULT']['Password'] = slippi_password
    config['DEFAULT']['Token'] = discord_token
    config['DEFAULT']['Full_database'] = database_path
    config['DEFAULT']['First_run'] = '0'
    with open(config_path, 'w') as configfile:
        config.write(configfile)


def main():
    logger.debug('Main ran')

    if not exists(config_path):
        logger.error('No config file, please create a ranked.ini')
        return

    try:
        if not config['DEFAULT'].getboolean('First_run', fallback=True):
            slippi_ranked.username = config['DEFAULT']['Username']
            slippi_ranked.password = config['DEFAULT']['Password']
        else:
            first_run()

    except Exception as e:
        logger.error(f'main: {e}')
        first_run()

    with do.create_con('database.db') as conn:
        database_setup.create_database(conn, conn.cursor())

    discord_bot.bot.run(config['DEFAULT']['Token'])


if __name__ == '__main__':
    main()

