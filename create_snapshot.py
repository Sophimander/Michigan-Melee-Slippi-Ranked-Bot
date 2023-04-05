import slippi.slippi_data
import database.database_operations as do
import os
import logging
import sys

logger = logging.getLogger('slippi_bot')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log.log')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)
formatter = logging.Formatter('%(asctime)s : %(module)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

database_path = os.environ.get('FULL_DATABASE')
logger.debug(f'create_snapshot: {database_path}')
with do.create_con(database_path) as conn:
    slippi.slippi_data.write_snapshot(conn)
