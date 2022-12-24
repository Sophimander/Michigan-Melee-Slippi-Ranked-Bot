import sqlite3
import datetime

from typing import Union
from sqlite3 import Error


db_path = 'database.db'


def replace_char_list(_old: str, _replacement: list,  _replace: str = '?') -> str:

    for i in _replacement:
        _old = _old.replace(_replace, str(i), 1)

    return _old


def create_con(path: str) -> sqlite3.Connection:
    try:
        con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        return con
    except Error as e:
        raise e


def create_user(connection: sqlite3.Connection, name: str, connect_code: str, uid: Union[int, None] = None) -> int:
    query = "INSERT INTO users VALUES (?, ?, ?)"
    query_param = [uid, name, connect_code.lower()]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return cur.lastrowid
    except Error as e:
        print(e)
        return 0


def create_date(connection: sqlite3.Connection, date: datetime.datetime = datetime.datetime.utcnow()) -> datetime:
    query = "INSERT INTO date VALUES (?)"
    query_param = [date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return date
    except Error as e:
        print(e)
        return 0


def create_elo(connection: sqlite3.Connection, uid: int, date: datetime.datetime, elo: float) -> int:
    query = "INSERT INTO elo VALUES (?, ?, ?)"
    query_param = [uid, date, elo]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return cur.lastrowid
    except Error as e:
        print(e)
        return 0


def create_rank(connection: sqlite3.Connection, uid: int, rank: str, date: datetime.datetime) -> int:
    query = "INSERT INTO rank VALUES (?, ?, ?)"
    query_param = [uid, rank, date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return cur.lastrowid
    except Error as e:
        print(e)
        return 0


def create_leaderboard(connection: sqlite3.Connection, uid: int, position: int, date: datetime.datetime) -> int:
    query = "INSERT INTO leaderboard VALUES (?, ?, ?)"
    query_param = [uid, position, date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return cur.lastrowid
    except Error as e:
        print(e)
        return 0


def create_win_loss(connection: sqlite3.Connection, uid: int, wins: int, loses: int, date: datetime.datetime) -> int:
    query = "INSERT INTO win_loss VALUES (?, ?, ?, ?)"
    query_param = [uid, wins, loses, date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return cur.lastrowid
    except Error as e:
        print(e)
        return 0


def update_user_connect_code(connection: sqlite3.Connection, uid: int, connect_code: str) -> bool:
    query = "UPDATE users SET connect_code = ? WHERE uid = ?"
    query_param = [connect_code, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        print(e)
        return False


def update_user_name(connection: sqlite3.Connection, uid: int, name: str) -> bool:
    query = "UPDATE users SET name = ? WHERE uid = ?"
    query_param = [name, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        print(e)
        return False


def get_all_users(connection: sqlite3.Connection):
    query = "SELECT * FROM users"
    query_param = []

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchall()

        if results is not None:
            return results
        else:
            return 0
    except Error as e:
        return 0


def get_latest_date(connection: sqlite3.Connection):
    query = "SELECT * FROM date ORDER BY date DESC"
    query_param = []

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        if results is not None:
            return datetime.datetime.strptime(results[0], "%Y-%m-%d %H:%M:%S.%f")
        return 0
    except Error as e:
        print(e)
        return 0


def get_leaderboard_by_date(connection: sqlite3.Connection, date: datetime.datetime):
    query = '''SELECT users.name, users.uid, leaderboard.position, elo.elo, 
                win_loss.wins, win_loss.losses, rank.rank, leaderboard.date 
                FROM users 
                INNER JOIN leaderboard ON users.uid = leaderboard.uid 
                INNER JOIN elo ON users.uid = elo.uid AND leaderboard.date = elo.date
                INNER JOIN rank ON users.uid = rank.uid AND leaderboard.date = rank.date
                INNER JOIN win_loss ON users.uid = win_loss.uid AND leaderboard.date = win_loss.date
                WHERE leaderboard.date=?
                ORDER BY leaderboard.position ASC'''
    query_param = [date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchall()

        if results is not None:
            return results
        return 0
    except Error as e:
        print(e)
        return 0


def get_user_by_uid(connection: sqlite3.Connection, uid: int):
    query = "SELECT * FROM users WHERE uid=?"
    query_param = [uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        if results is not None:
            return results
        return 0
    except Error as e:
        print(e)
        return 0


def get_user_by_connect_code(connection: sqlite3.Connection, connect_code: str):
    query = "SELECT * FROM users WHERE connect_code=?"
    query_param = [connect_code]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        if results is not None:
            return results
        return 0
    except Error as e:
        print(e)
        return 0


def is_connect_code_present(connection: sqlite3.Connection, connect_code: str) -> bool:
    query = "SELECT * FROM users WHERE connect_code=?"
    query_param = [connect_code.lower()]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        if results is not None:
            return True
        return False
    except Error as e:
        print(e)
        return False

