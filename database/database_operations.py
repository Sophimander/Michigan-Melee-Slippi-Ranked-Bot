import sqlite3
import datetime

from typing import Union
from sqlite3 import Error

import logging

logger = logging.getLogger(f'slippi_bot: {__name__}')

db_path = 'database.db'


def replace_char_list(_old: str, _replacement: list, _replace: str = '?') -> str:
    for i in _replacement:
        _old = _old.replace(_replace, str(i), 1)

    return _old


def create_con(path: str) -> sqlite3.Connection:
    logger.debug(f'create_con: {path}')
    try:
        con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        return con
    except Error as e:
        logger.error(e)
        raise e


def create_user(connection: sqlite3.Connection, name: str, connect_code: str,
                uid: Union[int, None] = None, rating_update_count: int = 0) -> int:
    logger.debug(f'create_user: {name}, {connect_code}, {uid}, {rating_update_count}')
    query = "INSERT INTO users VALUES (?, ?, ?, ?)"
    query_param = [uid, name, connect_code.lower()]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return 1
    except Error as e:
        logger.error(e)
        return 0


def create_date(connection: sqlite3.Connection, date: datetime.datetime = datetime.datetime.utcnow()) -> datetime:
    logger.debug(f'create_date: {date}')
    query = "INSERT INTO date VALUES (?)"
    query_param = [date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return date
    except Error as e:
        logger.error(e)
        return 0


def create_elo(connection: sqlite3.Connection, uid: int, date: datetime.datetime, elo: float) -> int:
    logger.debug(f'create_elo: {uid}, {date}, {elo}')
    query = "INSERT INTO elo VALUES (?, ?, ?)"
    query_param = [uid, date, elo]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return 1
    except Error as e:
        logger.error(e)
        return 0


def create_rank(connection: sqlite3.Connection, uid: int, rank: str, date: datetime.datetime) -> int:
    logger.debug(f'create_rank: {uid}, {rank}, {date}')
    query = "INSERT INTO rank VALUES (?, ?, ?)"
    query_param = [uid, rank, date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return 1
    except Error as e:
        logger.error(e)
        return 0


def create_leaderboard(connection: sqlite3.Connection, uid: int, position: int, date: datetime.datetime) -> int:
    logger.debug(f'create_leaderboard: {uid}, {position}, {date}')
    query = "INSERT INTO leaderboard VALUES (?, ?, ?)"
    query_param = [uid, position, date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return 1
    except Error as e:
        logger.error(e)
        return 0


def create_win_loss(connection: sqlite3.Connection, uid: int, wins: int, loses: int, date: datetime.datetime) -> int:
    logger.debug(f'create_win_loss: {uid}, {wins}, {loses}, {date}')
    query = "INSERT INTO win_loss VALUES (?, ?, ?, ?)"
    query_param = [uid, wins, loses, date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return 1
    except Error as e:
        logger.error(e)
        return 0


def update_user_connect_code(connection: sqlite3.Connection, uid: int, connect_code: str) -> bool:
    logger.debug(f'update_user_connect_code: {uid}, {connect_code}')
    query = "UPDATE users SET connect_code = ? WHERE uid = ?"
    query_param = [connect_code, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_user_name(connection: sqlite3.Connection, uid: int, name: str) -> bool:
    logger.debug(f'update_user_name: {uid}, {name}')
    query = "UPDATE users SET name = ? WHERE uid = ?"
    query_param = [name, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_user_uid(connection: sqlite3.Connection, uid: int, uid_new: int) -> bool:
    logger.debug(f'update_user_uid: {uid}, {uid_new}')
    query = "UPDATE users SET uid = ? WHERE uid = ?"
    query_param = [uid_new, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_user_rating_count(connection: sqlite3.Connection, uid: int, rating_count: int) -> bool:
    logger.debug(f'update_user_rating_count: {uid}, {rating_count}')
    query = "UPDATE users SET rating_update_count = ? WHERE uid = ?"
    query_param = [rating_count, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_elo_uid(connection: sqlite3.Connection, uid: int, uid_new: int) -> bool:
    logger.debug(f'update_elo_uid: {uid}, {uid_new}')
    query = "UPDATE elo SET uid = ? WHERE uid = ?"
    query_param = [uid_new, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_rank_uid(connection: sqlite3.Connection, uid: int, uid_new: int) -> bool:
    logger.debug(f'update_rank_uid: {uid}, {uid_new}')
    query = "UPDATE rank SET uid = ? WHERE uid = ?"
    query_param = [uid_new, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_win_loss_uid(connection: sqlite3.Connection, uid: int, uid_new: int) -> bool:
    logger.debug(f'update_win_loss_uid: {uid}, {uid_new}')
    query = "UPDATE win_loss SET uid = ? WHERE uid = ?"
    query_param = [uid_new, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def update_leaderboard_uid(connection: sqlite3.Connection, uid: int, uid_new: int) -> bool:
    logger.debug(f'update_leaderboard_uid: {uid}, {uid_new}')
    query = "UPDATE leaderboard SET uid = ? WHERE uid = ?"
    query_param = [uid_new, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        connection.commit()

        return True
    except Error as e:
        logger.error(e)
        return False


def get_all_users(connection: sqlite3.Connection):
    logger.debug(f'get_all_users')
    query = "SELECT * FROM users"
    query_param = []

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchall()

        logger.debug(f'results: {results}')

        if results is not None:
            return results
        else:
            return 0
    except Error as e:
        logger.error(e)
        return 0


def get_latest_date(connection: sqlite3.Connection):
    logger.debug(f'get_latest_date')
    query = "SELECT * FROM date ORDER BY date DESC"
    query_param = []

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return datetime.datetime.strptime(results[0], "%Y-%m-%d %H:%M:%S.%f")
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_leaderboard_by_date(connection: sqlite3.Connection, date: datetime.datetime):
    logger.debug(f'get_leaderboard_by_date: {date}')
    query = '''SELECT users.name, users.uid, leaderboard.position, latest_elo.elo, 
        latest_win_loss.wins, latest_win_loss.losses, latest_rank.rank, leaderboard.date 
FROM users 
INNER JOIN leaderboard ON users.uid = leaderboard.uid 
LEFT JOIN (
    SELECT elo.uid, elo.date, elo.elo 
    FROM elo 
    INNER JOIN (
        SELECT uid, MAX(date) AS date 
        FROM elo 
        GROUP BY uid
    ) AS latest_elo ON elo.uid = latest_elo.uid AND elo.date = latest_elo.date
) AS latest_elo ON users.uid = latest_elo.uid 
LEFT JOIN (
    SELECT rank.uid, rank.date, rank.rank 
    FROM rank 
    INNER JOIN (
        SELECT uid, MAX(date) AS date 
        FROM rank 
        GROUP BY uid
    ) AS latest_rank ON rank.uid = latest_rank.uid AND rank.date = latest_rank.date
) AS latest_rank ON users.uid = latest_rank.uid 
LEFT JOIN (
    SELECT win_loss.uid, win_loss.date, win_loss.wins, win_loss.losses 
    FROM win_loss 
    INNER JOIN (
        SELECT uid, MAX(date) AS date 
        FROM win_loss 
        GROUP BY uid
    ) AS latest_win_loss ON win_loss.uid = latest_win_loss.uid AND win_loss.date = latest_win_loss.date
) AS latest_win_loss ON users.uid = latest_win_loss.uid 
WHERE leaderboard.date = ?
ORDER BY leaderboard.position ASC'''
    query_param = [date]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchall()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_stats_by_date(connection: sqlite3.Connection, uid: int, date: datetime.datetime):
    logger.debug(f'get_user_stats_by_date: {uid}, {date}')
    query = 'SELECT users.uid, users.name, users.connect_code, leaderboard.position, elo.elo, win_loss.wins, win_loss.losses, rank.rank, leaderboard.date ' \
            'FROM users ' \
            'INNER JOIN leaderboard ON users.uid = leaderboard.uid ' \
            'INNER JOIN elo ON users.uid = elo.uid AND leaderboard.date = elo.date ' \
            'INNER JOIN rank ON users.uid = rank.uid AND leaderboard.date = rank.date ' \
            'INNER JOIN win_loss ON users.uid = win_loss.uid AND leaderboard.date = win_loss.date ' \
            'WHERE leaderboard.date=? AND users.uid=?'
    query_param = [date, uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_by_uid(connection: sqlite3.Connection, uid: int):
    logger.debug(f'get_user_by_uid: {uid}')
    query = "SELECT * FROM users WHERE uid=?"
    query_param = [uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_by_connect_code(connection: sqlite3.Connection, connect_code: str):
    logger.debug(f'get_user_by_connect_code: {connect_code}')
    query = "SELECT * FROM users WHERE connect_code=?"
    query_param = [connect_code]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_data_full(connection: sqlite3.Connection, uid: int):
    logger.debug(f'get_user_by_connect_code: {uid}')
    return get_user_stats_by_date(connection, uid, get_latest_date(connection))


def get_user_data_latest(connection: sqlite3.Connection, uid: int):
    logger.debug(f'get_user_stats_by_date: {uid}')
    query = '''
        SELECT 
        users.uid, 
        users.name, 
        users.connect_code, 
        leaderboard.position, 
        elo.elo, 
        win_loss.wins, 
        win_loss.losses, 
        rank.rank, 
        leaderboard.date,
        rank.date AS rank_date
        FROM 
            users 
        INNER JOIN 
            leaderboard ON users.uid = leaderboard.uid 
        INNER JOIN 
            elo ON users.uid = elo.uid AND leaderboard.date = elo.date 
        INNER JOIN 
            rank ON users.uid = rank.uid
        INNER JOIN 
            win_loss ON users.uid = win_loss.uid AND leaderboard.date = win_loss.date 
        WHERE 
            users.uid = ?
        ORDER BY 
            leaderboard.date DESC, rank_date DESC
        '''
    query_param = [uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_rank_latest(connection: sqlite3.Connection, uid: int):
    logger.debug(f'get_user_rank_latest: {uid}')
    query = "SELECT * FROM rank WHERE uid = ? ORDER BY date DESC"
    query_param = [uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_elo_latest(connection: sqlite3.Connection, uid: int):
    logger.debug(f'get_user_elo_latest: {uid}')
    query = "SELECT * FROM elo WHERE uid = ? ORDER BY date DESC"
    query_param = [uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def get_user_win_loss_latest(connection: sqlite3.Connection, uid: int):
    logger.debug(f'get_user_win_loss_latest: {uid}')
    query = "SELECT * FROM win_loss WHERE uid = ? ORDER BY date DESC"
    query_param = [uid]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return results
        return 0
    except Error as e:
        logger.error(e)
        return 0


def is_connect_code_present(connection: sqlite3.Connection, connect_code: str) -> bool:
    logger.debug(f'is_connect_code_present: {connect_code}')
    query = "SELECT * FROM users WHERE connect_code=?"
    query_param = [connect_code.lower()]

    try:
        cur = connection.cursor()
        cur.execute(query, query_param)
        results = cur.fetchone()

        logger.debug(f'results: {results}')
        if results is not None:
            return True
        return False
    except Error as e:
        logger.error(e)
        return False
