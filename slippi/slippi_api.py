import requests
from ratelimiter import RateLimiter
import logging
import re

import slippi.ranks as ranks
import slippi.data_response

logger = logging.getLogger(f'slippi_bot.{__name__}')

limiter = RateLimiter(max_calls=1, period=1)

slippi_url_prefix = "https://slippi.gg/user/"


def connect_code_to_html(connect_code):
    return connect_code.replace("#", "-")


def elo_sort(elem):
    return elem[4]


def elo_sort_new(elem):
    return elem.rating_ordinal


def is_valid_connect_code(connect_code):
    return re.match(r"^[a-zA-Z]{1,7}#[0-9]{1,7}$", connect_code) and len(connect_code) < 9


def get_player_data(connect_code: str):
    query = """
        fragment userProfilePage on User {
            displayName
            connectCode {
                code
                __typename
            }
            rankedNetplayProfile {
                id
                ratingOrdinal
                ratingUpdateCount
                wins
                losses
                dailyGlobalPlacement
                dailyRegionalPlacement
                continent
                characters {
                    id
                    character
                    gameCount
                    __typename
                }
                __typename
            }
            __typename
        }
        query AccountManagementPageQuery($cc: String!) {
            getConnectCode(code: $cc) {
                user {
                    ...userProfilePage
                    __typename
                }
                __typename
            }
        }
    """
    variables = {
        "cc": connect_code
    }
    payload = {
        "operationName": "AccountManagementPageQuery",
        "query": query,
        "variables": variables
    }
    headers = {
        "content-type": "application/json"
    }
    response = requests.post('https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql', json=payload, headers=headers)
    return response.json()


def get_player_data_throttled(connect_code):
    with limiter:
        return get_player_data(connect_code.upper())


def does_exist(player_data: dict):
    return player_data['data']['getConnectCode']


def get_player_data_cleaned(connect_code):
    player_data = get_player_data_throttled(connect_code)
    if does_exist(player_data):
        cleaned_data = slippi.data_response.Response(player_data)
        return cleaned_data


def extract_player_data(response):
    return response["data"]["getConnectCode"]["user"]["rankedNetplayProfile"]


def get_player_ranked_data_fast(connect_code: str):

    logger.debug(f'get_player_ranked_data_fast: {connect_code}')

    player_data = get_player_data_cleaned(connect_code)
    if not player_data:
        return None
    return [connect_code, ranks.get_rank(player_data.rating_ordinal, player_data.daily_regional_placement),
            player_data.rating_ordinal, player_data.wins, player_data.losses]


def get_player_ranked_data_extra(user):
    logger.debug(f'get_player_ranked_data_extra: {user}')

    uid = user[0]
    name = user[1]
    connect_code = user[2]

    player_data = get_player_data_cleaned(connect_code)
    if not player_data:
        return None

    elo_rating = player_data.rating_ordinal
    rank_text = ranks.get_rank(elo_rating, player_data.daily_regional_placement)
    wins = player_data.wins
    loses = player_data.wins
    if player_data.characters:
        character_url = player_data.characters[0].get_character_icon_url()
    else:
        character_url = slippi.data_response.slippi_character_url.replace('?', 0)
    return [uid, name, connect_code, rank_text, elo_rating, wins, loses, character_url]


def get_player_ranked_data(user):
    logger.debug(f'get_player_ranked_data: {user}')

    uid = user[0]
    name = user[1]
    connect_code = user[2]

    player_data = get_player_data_cleaned(connect_code)
    if not player_data:
        return None

    elo_rating = player_data.rating_ordinal
    rank_text = ranks.get_rank(elo_rating, player_data.daily_regional_placement)
    wins = player_data.wins
    loses = player_data.losses
    return [uid, name, connect_code, rank_text, elo_rating, wins, loses]
