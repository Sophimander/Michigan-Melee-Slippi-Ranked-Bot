import datetime

import slippi.slippi_api as sa
import slippi.ranks as ranks
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
    print(users)
    if not users:
        logger.error(f'Unable to get players')
        return ExitCode.FAILED_TO_GET_ALL_PLAYERS

    for individual in users:
        logger.debug(f'individual: {individual}')
        user_stats = sa.get_player_data_cleaned(individual[2])
        ranked_data.append(user_stats)
        logger.debug(f'{individual}: {user_stats}')
    return [users, ranked_data]


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
                                f"| {format(entry[3], '.1f')} ({entry[4]}/{entry[5]}) {entry[6]}")

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

    local_users = ranked_data[0]
    ranked_data_sep = ranked_data[1]

    write_rank_data(conn, ranked_data_sep, local_users, date)
    write_elo_data(conn, ranked_data_sep, local_users, date)
    write_win_loss_data(conn, ranked_data_sep, local_users, date)
    write_leaderboard_position(conn, ranked_data_sep, local_users, date)
    write_user_rating_count(conn, ranked_data_sep, local_users)


def write_leaderboard_position(conn: sqlite3.Connection, ranked_data, local_user, date: datetime.datetime):
    logger.debug(f'write_leaderboard_position')
    clean_ranked_data = [item for item in ranked_data if item is not None]
    clean_ranked_data.sort(reverse=True, key=sa.elo_sort_new)
    increment = 0
    for user in clean_ranked_data:
        logger.debug(f'user: {user}, {increment}')
        increment += 1
        user_index = ranked_data.index(user)
        do.create_leaderboard(conn, local_user[user_index][0], increment, date)


def write_rank_data(conn: sqlite3.Connection, ranked_data, local_user, date: datetime.datetime):
    logger.debug(f'write_rank_data')
    for user in ranked_data:
        local_index = ranked_data.index(user)
        logger.debug(f'write_rank_data: {user} {local_user[local_index]}')
        if user is not None:
            logger.debug(f'user: {user}')
            if user.rating_update_count > local_user[local_index][3]:
                do.create_rank(conn, local_user[local_index][0],
                               ranks.get_rank(user.rating_ordinal, user.daily_regional_placement), date)


def write_elo_data(conn: sqlite3.Connection, ranked_data, local_user, date: datetime.datetime):
    logger.debug(f'write_elo_data')
    for user in ranked_data:
        local_index = ranked_data.index(user)
        logger.debug(f'write_elo_data: {user} {local_user[local_index]}')
        if user is not None:
            logger.debug(f'user: {user}')
            if user.rating_update_count > local_user[local_index][3]:
                do.create_elo(conn, local_user[local_index][0], date, user.rating_ordinal)


def write_win_loss_data(conn: sqlite3.Connection, ranked_data, local_user, date: datetime.datetime):
    logger.debug(f'write_win_loss_data')
    for user in ranked_data:
        local_index = ranked_data.index(user)
        logger.debug(f'write_win_loss_data: {user} {local_user[local_index]}')
        if user is not None:
            logger.debug(f'user: {user}')
            if user.rating_update_count > local_user[local_index][3]:
                do.create_win_loss(conn, local_user[local_index][0], user.wins, user.losses, date)


def write_user_rating_count(conn: sqlite3.Connection, ranked_data, local_user):
    logger.debug(f'write_user_rating_count')
    for user in ranked_data:
        local_index = ranked_data.index(user)
        logger.debug(f'write_user_rating_count: {user} {local_user[local_index]}')
        if user is not None:
            logger.debug(f'user: {user}')
            if user.rating_update_count > local_user[local_index][3]:
                do.update_user_rating_count(conn, local_user[local_index][0], user.rating_update_count)


def create_user_entry(conn: sqlite3.Connection, uid: int, name: str, connect_code: str) -> ExitCode:
    logger.debug(f'create_user_entry: {uid}, {name}, {connect_code}')
    if not sa.is_valid_connect_code(connect_code.lower()):
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
