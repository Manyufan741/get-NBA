"""Seed file"""
from nba_core.shared.models import db
from nba_core.app import app

# Create all tables
db.drop_all()
db.create_all()
