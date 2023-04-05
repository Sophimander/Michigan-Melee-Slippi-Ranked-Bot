from dataclasses import dataclass, field
from typing import Union

import database.database_operations as do
import slippi.slippi_api as sa
import slippi.slippi_data as sd

import logging

logger = logging.getLogger(f'slippi_bot.{__name__}')


@dataclass
class User:
    uid: int
    connect_code: str = ''
    name: str = ''
    rank: str = ''
    position: int = 0
    elo: float = 0.0
    wins: int = 0
    losses: int = 0
    characters: list[str] = field(default_factory=list)

    def assign_data_local(self) -> sd.ExitCode:
        logger.debug(f'assign_local_data: {self}')

        with do.create_con(do.db_path) as conn:

            user_table = do.get_user_by_uid(conn, self.uid)
            if not user_table:
                logger.debug(f'Unable to get user table from database')
                return sd.ExitCode.FAILED_TO_GET_PLAYER

            self.connect_code = user_table[2]
            self.name = user_table[1]

            user_data = do.get_user_data_full(conn, self.uid)
            if not user_data:
                logger.debug(f'Unable to get full user data')
                return sd.ExitCode.FAILED_TO_GET_PLAYER

            self.position = user_data[3]
            self.elo = user_data[4]
            self.wins = user_data[5]
            self.losses = user_data[6]
            self.rank = user_data[7]

            logger.debug(f'{self}')
            return sd.ExitCode.USER_ASSIGNED_SUCCESSFULLY

    def assign_slippi_data(self, connect_code: str = None) -> sd.ExitCode:
        logger.debug(f'assign_slippi_data: {self}, {connect_code}')

        # If connect code or self.connect_code are not given attempt to fill with local data
        if not connect_code or not self.connect_code:

            with do.create_con(do.db_path) as conn:

                user_local = do.get_user_by_uid(conn, self.uid)
                if not user_local:
                    logger.debug(f'Unable to get user data')
                    return sd.ExitCode.FAILED_TO_GET_PLAYER

                self.connect_code = user_local[2]
                self.name = user_local[1]

        # If connect_code is given, assign it to self.connect_code
        elif connect_code:
            self.connect_code = connect_code

        # Validate connect_code
        if not sa.is_valid_connect_code(self.connect_code):
            logger.debug(f'Invalid connect code: {self.connect_code}')
            return sd.ExitCode.INVALID_CONNECT_CODE

        slippi_stats = sa.get_player_ranked_data_extra([self.uid, self.name, self.connect_code])
        if not slippi_stats:
            logger.debug(f'Unable to pull stats from slippi.gg')
            return sd.ExitCode.FAILED_TO_GET_PLAYER

        self.rank = slippi_stats[3]
        self.elo = slippi_stats[4]
        self.wins = slippi_stats[5]
        self.losses = slippi_stats[6]
        self.characters.append(slippi_stats[7])

        logger.debug(f'{self}')
        return sd.ExitCode.USER_ASSIGNED_SUCCESSFULLY


def get_user_local_uid (uid: int) -> Union[User, sd.ExitCode]:
    logger.debug(f'get_user_local: {uid}')

    with do.create_con(do.db_path) as conn:
        user_table = do.get_user_by_uid(conn, uid)
        if not user_table:
            logger.debug(f'Unable to get user table from database')
            return sd.ExitCode.FAILED_TO_GET_PLAYER

    return User(uid, user_table[2], user_table[1])


def get_user_local_cc (connect_code: str) -> Union[User, sd.ExitCode]:
    logger.debug(f'get_user_local: {connect_code}')

    with do.create_con(do.db_path) as conn:
        user_table = do.get_user_by_connect_code(conn, connect_code)
        if not user_table:
            logger.debug(f'Unable to get user table from database')
            return sd.ExitCode.FAILED_TO_GET_PLAYER

    return User(user_table[0], user_table[2], user_table[1])
