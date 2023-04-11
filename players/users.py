from dataclasses import dataclass, field
from typing import Union

import players.errors
import slippi.slippi_api as sa
import slippi.data_response as dr
import slippi.ranks as ranks

import logging

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class User:
    connect_code: str
    name: str = ''
    rank: str = ''
    rating_update_count: int = 0
    elo: float = 0.0
    wins: int = 0
    losses: int = 0
    characters: list[dr.SlippiCharacters] = field(default_factory=list)

    def assign_slippi_data(self):
        logger.debug(f'assign_slippi_data: {self}')

        # Validate connect_code
        if not sa.is_valid_connect_code(self.connect_code):
            logger.debug(f'Invalid connect code: {self.connect_code}')
            raise players.errors.InvalidConnectCode(self.connect_code)

        slippi_stats = sa.get_player_data_cleaned(self.connect_code)
        if not slippi_stats:
            logger.debug(f'Unable to pull stats from slippi.gg')
            raise players.errors.FailedToGetSlippiUserData([self.connect_code])

        self._assign_values(slippi_stats)

        logger.debug(f'{self}')

    def _assign_values(self, data: dr.Response):
        self.elo = data.rating_ordinal
        self.rank = ranks.get_rank(self.elo, data.daily_regional_placement)
        self.wins = data.wins
        self.losses = data.losses
        self.characters = data.characters

    '''
    def assign_slippi_api_data(self, connect_code: str = None):
        logger.debug(f'assign_slippi_api_data: {self}, {connect_code}')

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

        slippi_stats = sa.get_player_data_cleaned(self.connect_code)
        if not slippi_stats:
            logger.debug(f'Unable to pull stats from slippi api')
            return sd.ExitCode.FAILED_TO_GET_PLAYER

        self.elo = slippi_stats.rating_ordinal
        self.rank = ranks.get_rank(self.elo, slippi_stats.daily_regional_placement)
        self.wins = slippi_stats.wins
        self.losses = slippi_stats.losses
        self.rating_update_count = slippi_stats.rating_update_count
        if slippi_stats.characters:
            self.characters.append(sa.get_character_url(slippi_stats.characters[0].character))

        logger.debug(f'{self}')
        return sd.ExitCode.USER_ASSIGNED_SUCCESSFULLY
        '''
