import slippi.slippi_data
import database.database_operations as do
import sqlite3

conn = do.create_con('database.db')
slippi.slippi_data.write_snapshot(conn)
conn.close()