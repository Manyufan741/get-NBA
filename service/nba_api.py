import requests
from requests.exceptions import HTTPError

BASE_URL = "https://www.balldontlie.io/api/v1"
seasons = [num for num in range(1979, 2020)]


class PlayerStats:
    def __init__(self, pts, reb, ast, stl, blk):
        self.pts = pts
        self.reb = reb
        self.ast = ast
        self.stl = stl
        self.blk = blk


def make_requests(url, query):
    try:
        response = requests.get(url, params=query)
        return response.json()
    except:
        return "Wrong/invalid request to API."


def search_player(player_full_name):
    search_player_URL = f"{BASE_URL}/players"
    query = {"search": player_full_name}

    response = make_requests(search_player_URL, query)
    data = response['data']

    if data:
        player_id = data[0]['id']
        results = get_player_avg_stat(player_id)
        return results
    else:
        return None


def get_player_avg_stat(id):
    get_player_avg_stat_URL = f"{BASE_URL}/season_averages"
    results = []
    for season in seasons:
        query = {"player_ids[]": id, "season": season}

        response = make_requests(get_player_avg_stat_URL, query)
        data = response['data']

        if data:
            player_data = data[0]
            results.append({"season": player_data['season'], "games_played": player_data['games_played'], "pts": player_data['pts'],
                            "reb": player_data['reb'], "ast": player_data['ast'], "stl": player_data['stl'], "blk": player_data['blk']})

    return results


def search_player_adv(player_full_name, start_date, end_date, playerstats):
    search_player_URL = f"{BASE_URL}/players"
    query = {"search": player_full_name}

    response = make_requests(search_player_URL, query)
    data = response['data']

    if data:
        player_id = data[0]['id']
        results = get_player_advanced_stat(
            player_id, start_date, end_date, playerstats)
        return results
    else:
        return None


def get_player_advanced_stat(player_id, start_date, end_date, playerstats):
    search_stats_URL = f"{BASE_URL}/stats"
    query = {"start_date": start_date,
             "end_date": end_date, "player_ids[]": player_id, "per_page": 100}
    target_stats = [playerstats.pts, playerstats.reb,
                    playerstats.ast, playerstats.stl, playerstats.blk]
    results = []

    response = make_requests(search_stats_URL, query)
    data = response['data']
    total_pages = response['meta']['total_pages']

    if data:
        for page in range(1, total_pages + 1):
            query_with_page = {"start_date": start_date, "end_date": end_date,
                               "player_ids[]": player_id, "per_page": 100, "page": page}

            response_with_page = make_requests(
                search_stats_URL, query_with_page)
            data_with_page = response_with_page['data']
            for game in data_with_page:
                player_actual_stats = [
                    game.get('pts', 0), game.get('reb', 0), game.get('ast', 0), game.get('stl', 0), game.get('blk', 0)]
                passed = check_playerstat_against_criteria(
                    player_actual_stats, target_stats)
                if passed:
                    results.append({"game_date": game['game']['date'], "playing_for": game['team']['name'],
                                    "pts": game['pts'], "reb": game['reb'], "ast": game['ast'], "stl": game['stl'], "blk": game['blk']})

    return results


def check_playerstat_against_criteria(player_actual_stats, target_stats):
    for i in range(len(player_actual_stats)):
        if not isinstance(player_actual_stats[i], int):
            player_actual_stats[i] = 0
        if player_actual_stats[i] < target_stats[i]:
            return False
    return True
