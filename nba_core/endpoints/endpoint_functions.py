from flask import redirect, render_template, request, flash, session, g
from sqlalchemy.exc import IntegrityError

from shared.models import db, User
from shared.forms import SignupForm, LoginForm, PlayerForm, AdvancedForm
from service.nba_api import search_player, search_player_adv, PlayerStats
from dal.database import signup, get_leader_stats

CURR_USER_KEY = "curr_user"


def before_request_endpoint():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def after_request_endpoint(req):
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


def home_endpoint():
    result = get_leader_stats()
    if g.user:
        return render_template('search_home.html', scoring_leaders=result['scoring_leaders'], rebounding_leaders=result['rebounding_leaders'], assisting_leaders=result['assisting_leaders'], stealing_leaders=result['stealing_leaders'], blocking_leaders=result['blocking_leaders'])
    else:
        return render_template('home-anon.html', scoring_leaders=result['scoring_leaders'], rebounding_leaders=result['rebounding_leaders'], assisting_leaders=result['assisting_leaders'], stealing_leaders=result['stealing_leaders'], blocking_leaders=result['blocking_leaders'])


def do_login(user):
    """Log in a user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout a user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def user_signup_endpoint():
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


def login_endpoint():
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


def logout_endpoint():
    do_logout()
    flash("Succuessfully logged out!", 'success')
    return redirect('/')


def get_player_stats_endpoint():
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


def get_adv_player_stats_endpoint():
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
        playerstats = PlayerStats(pts, reb, ast, stl, blk)
        results = search_player_adv(
            player_full_name, start_date, end_date, playerstats)

        if results is None:
            flash("Player not found", 'danger')
            return redirect('/api/adv-player-stats')
        else:
            return render_template('players/adv_stat.html', results=results, name=player_full_name)

    else:
        return render_template('players/adv_stat_search.html', form=form)
