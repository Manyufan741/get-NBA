import random
import requests
import os
from models import db, User
from Database import connect_db, signup
from API_interact import search_player, search_player_adv
from flask import Flask, redirect, render_template, request, jsonify, flash, session, g
from forms import SignupForm, LoginForm, PlayerForm, AdvancedForm
from sqlalchemy.exc import IntegrityError
from requests.exceptions import HTTPError

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql:///nba-users')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'oneonetwotwo')

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
    """Log in a user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout a user."""

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
def user_signup():
    """Handle user signup."""
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = signup(
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
    """Handle login of user."""
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
    return redirect('/')


######################################################################
# player search routes

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
        return render_template('players/career_stat_search.html', form=form)


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
        results = search_player_adv(
            player_full_name, start_date, end_date, pts, reb, ast, stl, blk)

        if results is None:
            flash("Player not found", 'danger')
            return redirect('/api/adv-player-stats')
        else:
            return render_template('players/adv_stat.html', results=results, name=player_full_name)

    else:
        return render_template('players/adv_stat_search.html', form=form)
