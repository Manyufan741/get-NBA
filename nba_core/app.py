import os

from flask import Flask

from dal.database import connect_db
from endpoints.endpoint_functions import before_request_endpoint, after_request_endpoint, user_signup_endpoint, home_endpoint, login_endpoint, logout_endpoint, get_player_stats_endpoint, get_adv_player_stats_endpoint

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql:///nba-users')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'oneonetwotwo')

connect_db(app)


@app.before_request
def add_user_to_g():
    """If user is logged in, add curr user to Flask global."""
    before_request_endpoint()


@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""
    return after_request_endpoint(req)

######################################################################
# General routes


@app.route('/')
def home():
    # get the season leaders' stats that should be stored in database
    return home_endpoint()


@app.route('/signup', methods=["GET", "POST"])
def user_signup():
    """Handle user signup."""
    return user_signup_endpoint()


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle login of user."""
    return login_endpoint()


@app.route('/logout')
def logout():
    """Handle logout of user."""
    return logout_endpoint()


######################################################################
# player search routes

@app.route('/api/get-player-stats', methods=["GET", "POST"])
def get_player_stats():
    return get_player_stats_endpoint()


@app.route('/api/adv-player-stats', methods=["GET", "POST"])
def get_adv_player_stats():
    return get_adv_player_stats_endpoint()
