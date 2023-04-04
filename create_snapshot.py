import slippi.slippi_data
import database.database_operations as do
import os

with do.create_con(os.environ.get('FULL_DATABASE')) as conn:
    slippi.slippi_data.write_snapshot(conn)
