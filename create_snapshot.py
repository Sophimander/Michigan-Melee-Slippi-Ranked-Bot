import slippi.slippi_data
import database.database_operations as do
import configparser

config_path = 'ranked.ini'
config = configparser.ConfigParser()
config.read(config_path)

with do.create_con(config['DEFAULT']['Full_database']) as conn:
    slippi.slippi_data.write_snapshot(conn)
