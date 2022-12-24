import datetime

import slippi.slippi_ranked as sr
import sqlite3
import database.database_operations as do

from enum import Enum


class ExitCode(Enum):
    INVALID_CONNECT_CODE = 1
    CONNECT_CODE_ALREADY_EXISTS = 2
    USER_ALREADY_EXISTS = 3
    USER_CREATED_SUCCESSFULLY = 4
    USER_CREATION_FAILED = 5
    FAILED_TO_GET_ALL_PLAYERS = 6
    FAILED_TO_CREATE_DATE = 7
    FAILED_TO_GET_DATE = 8
    FAILED_TO_GET_LEADERBOARD = 9


def get_all_users_ranked_data(conn: sqlite3.Connection):
    ranked_data = []
    users = do.get_all_users(conn)

    if not users:
        return ExitCode.FAILED_TO_GET_ALL_PLAYERS

    for individual in users:
        user_stats = sr.get_player_ranked_data(individual)
        if user_stats is not False:
            ranked_data.append(user_stats)

    return ranked_data


def generate_leaderboard_text(conn: sqlite3.Connection):
    latest_date = do.get_latest_date(conn)
    if not latest_date:
        return ExitCode.FAILED_TO_GET_DATE

    leaderboard_data = do.get_leaderboard_by_date(conn, latest_date)
    if not leaderboard_data:
        return ExitCode.FAILED_TO_GET_LEADERBOARD

    leaderboard_text = []
    for entry in leaderboard_data:
        leaderboard_text.append(f"{entry[2]}. {entry[0]} | {entry[3]} ({entry[4]}/{entry[5]}) {entry[6]}\n")

    return leaderboard_text


def write_snapshot(conn: sqlite3.Connection):
    date = datetime.datetime.utcnow()
    if not do.create_date(conn, date):
        return ExitCode.FAILED_TO_CREATE_DATE

    ranked_data = get_all_users_ranked_data(conn)
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
    if not sr.is_valid_connect_code(connect_code.lower()):
        return ExitCode.INVALID_CONNECT_CODE

    if do.is_connect_code_present(conn, connect_code.lower()):
        return ExitCode.CONNECT_CODE_ALREADY_EXISTS

    if do.get_user_by_uid(conn, uid):
        return ExitCode.USER_ALREADY_EXISTS

    results = do.create_user(conn, name, connect_code.lower(), uid)
    if results:
        return ExitCode.USER_CREATED_SUCCESSFULLY

    return ExitCode.USER_CREATION_FAILED
