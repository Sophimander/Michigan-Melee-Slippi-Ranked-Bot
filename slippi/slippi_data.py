import datetime

import slippi.slippi_ranked as sr
import sqlite3
import database.database_operations as do

from enum import Enum

import logging

logger = logging.getLogger(f'slippi_bot.{__name__}')


class ExitCode(Enum):
    INVALID_CONNECT_CODE = 1
    CONNECT_CODE_ALREADY_EXISTS = 2
    USER_ALREADY_EXISTS = 3
    USER_CREATED_SUCCESSFULLY = 4
    USER_CREATION_FAILED = 5
    FAILED_TO_GET_PLAYER = 6
    FAILED_TO_GET_ALL_PLAYERS = 7
    FAILED_TO_CREATE_DATE = 8
    FAILED_TO_GET_DATE = 9
    FAILED_TO_GET_LEADERBOARD = 10
    USER_ASSIGNED_SUCCESSFULLY = 11


def generate_whitespace(n):
    return " " * n


def get_all_users_ranked_data(conn: sqlite3.Connection):
    logger.debug(f'get_all_users_ranked_data')
    ranked_data = []
    users = do.get_all_users(conn)

    if not users:
        logger.error(f'Unable to get players')
        return ExitCode.FAILED_TO_GET_ALL_PLAYERS

    for individual in users:
        user_stats = sr.get_player_ranked_data(individual)
        logger.debug(f'{individual}: {user_stats}')
        if user_stats is not False:
            ranked_data.append(user_stats)

    return ranked_data


def generate_leaderboard_text(conn: sqlite3.Connection):
    logger.debug('generate_leaderboard_text')
    latest_date = do.get_latest_date(conn)
    logger.debug(f'latest_date: {latest_date}')
    if not latest_date:
        return ExitCode.FAILED_TO_GET_DATE

    leaderboard_data = do.get_leaderboard_by_date(conn, latest_date)
    logger.debug(f'leaderboard_data: {leaderboard_data}')
    if not leaderboard_data:
        return ExitCode.FAILED_TO_GET_LEADERBOARD

    leaderboard_text = []
    for entry in leaderboard_data:
        logger.debug(f'entry: {entry}')
        base_whitespace = 13
        whitespace_amount_front = 2 if entry[2] <= 9 else 1
        whitespace_amount = (base_whitespace - len(entry[0]))
        leaderboard_text.append(f"{entry[2]}."
                                f"{generate_whitespace(whitespace_amount_front)}{entry[0]}"
                                f"{generate_whitespace(whitespace_amount)}"
                                f"| {entry[3]} ({entry[4]}/{entry[5]}) {entry[6]}")

    return leaderboard_text


def write_snapshot(conn: sqlite3.Connection):
    logger.debug(f'write_snapshot')
    date = datetime.datetime.utcnow()
    logger.debug(f'date: {date}')
    if not do.create_date(conn, date):
        return ExitCode.FAILED_TO_CREATE_DATE

    ranked_data = get_all_users_ranked_data(conn)
    logger.debug(f'ranked_data: {ranked_data}')
    if ranked_data == ExitCode.FAILED_TO_GET_ALL_PLAYERS:
        return ExitCode.FAILED_TO_GET_ALL_PLAYERS

    write_rank_data(conn, ranked_data, date)
    write_elo_data(conn, ranked_data, date)
    write_win_loss_data(conn, ranked_data, date)
    write_leaderboard_position(conn, ranked_data, date)


def write_leaderboard_position(conn: sqlite3.Connection, ranked_data, date: datetime.datetime):
    ranked_data.sort(reverse=True, key=sr.elo_sort)
    increment = 0
    for user in ranked_data:
        increment += 1
        do.create_leaderboard(conn, user[0], increment, date)


def write_rank_data(conn: sqlite3.Connection, ranked_data, date: datetime.datetime):
    for user in ranked_data:
        do.create_rank(conn, user[0], user[3], date)


def write_elo_data(conn: sqlite3.Connection, ranked_data, date: datetime.datetime):
    for user in ranked_data:
        do.create_elo(conn, user[0], date, user[4])


def write_win_loss_data(conn: sqlite3.Connection, ranked_data, date: datetime.datetime):
    for user in ranked_data:
        do.create_win_loss(conn, user[0], user[5], user[6], date)


def create_user_entry(conn: sqlite3.Connection, uid: int, name: str, connect_code: str) -> ExitCode:
    logger.debug(f'create_user_entry: {uid}, {name}, {connect_code}')
    if not sr.is_valid_connect_code(connect_code.lower()):
        return ExitCode.INVALID_CONNECT_CODE

    if do.is_connect_code_present(conn, connect_code.lower()):
        return ExitCode.CONNECT_CODE_ALREADY_EXISTS

    if do.get_user_by_uid(conn, uid):
        return ExitCode.USER_ALREADY_EXISTS

    results = do.create_user(conn, name, connect_code.lower(), uid)
    logger.debug(f'results: {results}')
    if results:
        return ExitCode.USER_CREATED_SUCCESSFULLY

    return ExitCode.USER_CREATION_FAILED
