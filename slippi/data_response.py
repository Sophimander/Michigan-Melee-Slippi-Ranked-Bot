from dataclasses import dataclass, field

import logging

logger = logging.getLogger(f'slippi_bot.{__name__}')


@dataclass
class SlippiCharacters:
    id: int
    character: str
    game_count: int


@dataclass
class Response:
    display_name: str
    connect_code: str
    id: int
    rating_ordinal: float
    rating_update_count: int
    wins: int
    losses: int
    daily_global_placement: int
    daily_regional_placement: int
    continent: str
    characters: list[SlippiCharacters]

    def __init__(self, data: dict):
        self.display_name = data['data']['getConnectCode']['user']['displayName']
        self.connect_code = data['data']['getConnectCode']['user']['connectCode']['code']
        self.id = int(data['data']['getConnectCode']['user']['rankedNetplayProfile']['id'], 16)
        self.rating_ordinal = data['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal'] or 0
        self.rating_update_count = \
            data['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingUpdateCount'] or 0
        self.wins = data['data']['getConnectCode']['user']['rankedNetplayProfile']['wins'] or 0
        self.losses = data['data']['getConnectCode']['user']['rankedNetplayProfile']['losses'] or 0
        self.daily_global_placement = data['data']['getConnectCode']['user']['rankedNetplayProfile'][
                                          'dailyGlobalPlacement']
        self.daily_regional_placement = data['data']['getConnectCode']['user']['rankedNetplayProfile'][
                                            'dailyRegionalPlacement']
        self.continent = data['data']['getConnectCode']['user']['rankedNetplayProfile']['continent']

        characters_data = data['data']['getConnectCode']['user']['rankedNetplayProfile']['characters']
        self.characters = []
        for character_data in characters_data:
            character_id = character_data['id']
            character_name = character_data['character']
            game_count = character_data['gameCount']
            self.characters.append(SlippiCharacters(character_id, character_name, game_count))

