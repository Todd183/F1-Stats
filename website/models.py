from . import db
from flask_login import UserMixin
from sqlalchemy import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    usr_name = db.Column(db.String(150))
    constructor = db.Column(db.String(150))
    current_race = db.Column(db.Integer)
