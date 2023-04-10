

def create_database(conn, c):
    # Create the users table
    c.execute('''CREATE TABLE IF NOT EXISTS 
            users (
                uid INTEGER PRIMARY KEY NOT NULL, 
                name TEXT, 
                connect_code TEXT UNIQUE,
                rating_update_count INTEGER NOT NULL DEFAULT 0)''')

    # Create the date table
    c.execute('''CREATE TABLE IF NOT EXISTS 
            date (
                date DATETIME PRIMARY KEY)''')

    # Create the elo table
    c.execute('''CREATE TABLE IF NOT EXISTS 
            elo (
                uid INTEGER,
                date DATETIME,
                elo FLOAT,
                PRIMARY KEY (uid, date),
                FOREIGN KEY (uid) REFERENCES users (uid),
                FOREIGN KEY (date) REFERENCES date (date))''')

    # Create the rank table
    c.execute('''CREATE TABLE IF NOT EXISTS
            rank (
                uid INTEGER,
                rank TEXT,
                date DATETIME,
                PRIMARY KEY (uid, date),
                FOREIGN KEY (uid) REFERENCES users (uid),
                FOREIGN KEY (date) REFERENCES date (date))''')

    # Create the leaderboard table
    c.execute('''CREATE TABLE IF NOT EXISTS
            leaderboard (
                uid INTEGER,
                position INTEGER,
                date DATETIME,
                PRIMARY KEY (uid, date),
                FOREIGN KEY (uid) REFERENCES users (uid),
                FOREIGN KEY (date) REFERENCES date (date))''')

    # Create the leaderboard table
    c.execute('''CREATE TABLE IF NOT EXISTS
            win_loss (
                uid INTEGER,
                wins INTEGER,
                losses INTEGER,
                date DATETIME,
                PRIMARY KEY (uid, date),
                FOREIGN KEY (uid) REFERENCES users (uid),
                FOREIGN KEY (date) REFERENCES date (date))''')

    # Save the changes and close the connection
    conn.commit()
