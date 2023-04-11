import slippi.slippi_data
import database.database_operations as do
import os
import logging
import sys

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

database_path = 'database.db'
logger.debug(f'create_snapshot: {database_path}')
with do.create_con(database_path) as conn:
    slippi.slippi_data.write_snapshot(conn)
