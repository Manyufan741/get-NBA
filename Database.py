from models import db, User
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('UTF-8')


def signup(username, password, first_name, last_name):
    """Sign up user.
    Hashes password and adds user to system.
    """
    hashed_pwd = hash_password(password)

    user = User(
        username=username,
        password=hashed_pwd,
        first_name=first_name,
        last_name=last_name
    )

    db.session.add(user)
    return user
