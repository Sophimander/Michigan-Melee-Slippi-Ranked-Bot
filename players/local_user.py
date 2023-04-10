import logging
from dataclasses import dataclass
from typing import Optional

import database.database_operations as do
import players.errors
import slippi.slippi_data as sd
from players.users import User

logger = logging.getLogger(f'slippi_bot.{__name__}')


@dataclass(kw_only=True)
class LocalUser(User):
    """Class for handling specifically Users, with data in the local database"""
    id: int
    position: int = 0

    def assign_data_local(self) -> sd.ExitCode:
        logger.debug(f'assign_local_data: {self}')

        with do.create_con(do.db_path) as conn:

            user_table = do.get_user_by_uid(conn, self.id)
            if not user_table:
                logger.debug(f'Unable to get user table from database')
                raise players.errors.FailedToGetLocalUserData([self.id, self.connect_code])

            self.connect_code = user_table[2]
            self.name = user_table[1]

            user_data = do.get_user_data_latest(conn, self.id)
            if not user_data:
                logger.debug(f'Unable to get full user data')
                raise players.errors.FailedToGetLocalUserData([self.id, self.connect_code])

            self.position = user_data[3]
            self.elo = user_data[4]
            self.wins = user_data[5]
            self.losses = user_data[6]
            self.rank = user_data[7]

            logger.debug(f'{self}')
            return sd.ExitCode.USER_ASSIGNED_SUCCESSFULLY


def create_local_user(uid: int) -> LocalUser:
    return LocalUser(id=uid, connect_code='')


def get_user_local_uid(uid: int) -> LocalUser:
    logger.debug(f'get_user_local: {uid}')

    with do.create_con(do.db_path) as conn:
        user_table = do.get_user_by_uid(conn, uid)
        if not user_table:
            logger.debug(f'Unable to get user table from database')
            raise players.errors.FailedToGetLocalUserData(uid)

    return LocalUser(id=uid, connect_code=user_table[2], name=user_table[1])


def get_user_local_cc(connect_code: str) -> LocalUser:
    logger.debug(f'get_user_local: {connect_code}')

    with do.create_con(do.db_path) as conn:
        user_table = do.get_user_by_connect_code(conn, connect_code)
        if not user_table:
            logger.debug(f'Unable to get user table from database')
            raise players.errors.FailedToGetLocalUserData(connect_code)

    return LocalUser(id=user_table[0], connect_code=connect_code, name=user_table[1])


def get_user_local(uid: int = 0, cc: str = '') -> Optional[LocalUser]:
    if uid:
        return get_user_local_uid(uid)
    elif str:
        return get_user_local_cc(cc)
    return None
