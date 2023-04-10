from dataclasses import dataclass, field

import logging

logger = logging.getLogger(f'slippi_bot.{__name__}')


slippi_character_url = 'https://slippi.gg/images/characters/stock-icon-?-0.png'


SlippiCharacterIcon = {
    'CAPTAIN_FALCON': 1,
    'DONKEY_KONG': 0,
    'FOX': 2,
    'GAME_AND_WATCH': 3,
    'KIRBY': 4,
    'BOWSER': 5,
    'LINK': 6,
    'LUIGI': 7,
    'MARIO': 8,
    'MARTH': 9,
    'MEWTWO': 10,
    'NESS': 11,
    'PEACH': 12,
    'PIKACHU': 13,
    'ICE_CLIMBERS': 14,
    'JIGGLYPUFF': 15,
    'SAMUS': 16,
    'YOSHI': 17,
    'ZELDA': 18,
    'SHEIK': 19,
    'FALCO': 20,
    'YOUNG_LINK': 21,
    'DR_MARIO': 22,
    'ROY': 23,
    'PICHU': 24,
    'GANONDORF': 25
}


@dataclass
class SlippiCharacters:
    id: int
    character: str
    game_count: int

    def get_character_icon_url(self):
        return slippi_character_url.replace('?', str(SlippiCharacterIcon.get(self.character)))


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

