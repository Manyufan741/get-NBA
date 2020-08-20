from flask import Flask, redirect, render_template, request, jsonify, flash
import requests
from requests.exceptions import HTTPError

BASE_URL = "https://www.balldontlie.io/api/v1"
seasons = [num for num in range(1979, 2020)]


def search_player(player_full_name):
    search_player_URL = f"{BASE_URL}/players"
    query = {"search": player_full_name}
    try:
        response = requests.get(
            search_player_URL, params=query)
        json_response = response.json()['data']
        if json_response:
            player_id = json_response[0]['id']
            results = get_player_avg_stat(player_id)
            return results
        else:
            return None

    except HTTPError:
        flash("HTTP Error/Page not found", 'danger')
        return redirect('/')

    except:
        flash("Wrong request!", 'danger')
        return redirect('/')


def get_player_avg_stat(id):
    get_player_avg_stat_URL = f"{BASE_URL}/season_averages"
    results = []
    for season in seasons:
        query = {"player_ids[]": id, "season": season}
        try:
            response = requests.get(get_player_avg_stat_URL, params=query)
            json_response = response.json()['data']
            if json_response:
                player_data = json_response[0]
                results.append({"season": player_data['season'], "games_played": player_data['games_played'], "pts": player_data['pts'],
                                "reb": player_data['reb'], "ast": player_data['ast'], "stl": player_data['stl'], "blk": player_data['blk']})

        except HTTPError:
            flash("HTTP Error/Page not found", 'danger')
            return redirect('/')

    return results


def search_player_adv(player_full_name, start_date, end_date, tgt_pts, tgt_reb, tgt_ast, tgt_stl, tgt_blk):
    search_player_URL = f"{BASE_URL}/players"
    query = {"search": player_full_name}
    try:
        response = requests.get(
            search_player_URL, params=query)
        json_response = response.json()['data']
        if json_response:
            #player is found
            player_id = json_response[0]['id']
            results = get_player_advanced_stat(
                player_id, start_date, end_date, tgt_pts, tgt_reb, tgt_ast, tgt_stl, tgt_blk)
            return results

        else:
            return None

    except HTTPError:
        flash("HTTP Error/Page not found", 'danger')
        return redirect('/')

    except:
        flash("Wrong request!", 'danger')
        return redirect('/')


def get_player_advanced_stat(player_id, start_date, end_date, tgt_pts, tgt_reb, tgt_ast, tgt_stl, tgt_blk):
    search_stats_URL = f"{BASE_URL}/stats"
    query = {"start_date": start_date,
             "end_date": end_date, "player_ids[]": player_id, "per_page": 100}
    target_stats = [tgt_pts, tgt_reb, tgt_ast, tgt_stl, tgt_blk]
    results = []
    try:
        response = requests.get(
            search_stats_URL, params=query)
        json_response = response.json()['data']
        total_pages = response.json()['meta']['total_pages']

        if json_response:
            # If a player did play in the given time frame
            for page in range(1, total_pages + 1):
                query_with_page = {"start_date": start_date, "end_date": end_date,
                                   "player_ids[]": player_id, "per_page": 100, "page": page}

                response_with_page = requests.get(
                    search_stats_URL, params=query_with_page)
                json_response_with_page = response_with_page.json()['data']

                for game in json_response_with_page:
                    player_actual_stats = [
                        game.get('pts', 0), game.get('reb', 0), game.get('ast', 0), game.get('stl', 0), game.get('blk', 0)]
                    passed = check_playerstat_against_criteria(
                        player_actual_stats, target_stats)
                    if passed:
                        results.append({"game_date": game['game']['date'], "playing_for": game['team']['name'],
                                        "pts": game['pts'], "reb": game['reb'], "ast": game['ast'], "stl": game['stl'], "blk": game['blk']})

            return results

        else:
            return results

    except HTTPError:
        flash("HTTP Error/Page not found", 'danger')
        return redirect('/')

    except:
        flash("Wrong request!", 'danger')
        return redirect('/')


def check_playerstat_against_criteria(player_actual_stats, target_stats):
    for i in range(len(player_actual_stats)):
        if not isinstance(player_actual_stats[i], int):
            player_actual_stats[i] = 0
        if player_actual_stats[i] < target_stats[i]:
            return False
    return True
