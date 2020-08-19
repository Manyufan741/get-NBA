from flask import Flask, redirect, render_template, request, jsonify, flash, session, g
from models import db, connect_db, User
from forms import SignupForm, LoginForm, PlayerForm, AdvancedForm
from werkzeug.datastructures import MultiDict
from sqlalchemy.exc import IntegrityError
import random
import requests
from requests.exceptions import HTTPError

CURR_USER_KEY = "curr_user"
BASE_URL = "https://www.balldontlie.io/api/v1"
# FREE_NBA_API_KEY = "4dc0a5e462mshd4ea55091483ef9p13ae14jsneacfe9e1969b"

seasons = [num for num in range(1979, 2020)]

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nba-users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "oneonetwotwo"

connect_db(app)
db.create_all()


@app.before_request
def add_user_to_g():
    """If user is logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

######################################################################
# General routes


@app.route('/')
def home():
    if g.user:
        return render_template('search_home.html')
    else:
        return render_template('home-anon.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("Succuessfully logged out!", 'success')
    return redirect('/login')


######################################################################
# player search routes

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


@app.route('/api/get-player-stats', methods=["GET", "POST"])
def get_player_stats():
    form = PlayerForm()
    if form.validate_on_submit():
        player_full_name = form.first_name.data + ' ' + form.last_name.data
        results = search_player(player_full_name)

        if results is None:
            flash("Player not found", 'danger')
            return redirect('/api/get-player-stats')
        else:
            return render_template('players/stat.html', results=results, name=player_full_name)

    else:
        # flash("Invalid search!", 'danger')
        return render_template('players/career_stat_search.html', form=form)


def search_player_adv(player_full_name, start_date, end_date, tgt_pts, tgt_reb, tgt_ast, tgt_stl, tgt_blk):
    search_player_URL = f"{BASE_URL}/players"
    query = {"search": player_full_name}
    try:
        response = requests.get(
            search_player_URL, params=query)
        json_response = response.json()['data']
        if json_response:
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
             "end_date": end_date, "player_ids[]": player_id}
    target_stats = [tgt_pts, tgt_reb, tgt_ast, tgt_stl, tgt_blk]
    results = []
    try:
        response = requests.get(
            search_stats_URL, params=query)
        json_response = response.json()['data']

        if json_response:
            # If a player did play in the given time frame
            for game in json_response:
                player_actual_stats = [
                    game['pts'], game['reb'], game['ast'], game['stl'], game['blk']]
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
        if player_actual_stats[i] < target_stats[i]:
            return False
    return True


@app.route('/api/adv-player-stats', methods=["GET", "POST"])
def get_adv_player_stats():
    form = AdvancedForm()
    if form.validate_on_submit():
        player_full_name = form.first_name.data + ' ' + form.last_name.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        pts = form.pts.data or 0
        reb = form.reb.data or 0
        ast = form.ast.data or 0
        stl = form.stl.data or 0
        blk = form.blk.data or 0
        print("NAME", player_full_name)
        print("TIME FRAME", start_date, end_date)
        print("PTS", pts)
        print("REB", reb)
        print("AST", ast)
        print("STL", stl)
        print("BLK", blk)
        results = search_player_adv(
            player_full_name, start_date, end_date, pts, reb, ast, stl, blk)

        if results is None:
            flash("Player not found", 'danger')
            return redirect('/api/adv-player-stats')
        else:
            return render_template('players/adv_stat.html', results=results, name=player_full_name)

    else:
        #flash("Invalid search!", 'danger')
        return render_template('players/adv_stat_search.html', form=form)
