from . import db
from flask_login import UserMixin
from sqlalchemy import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # lower case here !!


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    usr_name = db.Column(db.String(150))
    # notes = db.relationship("Note")  # capital here !!
    # transaction = db.relationship("Transaction")
    constructor = db.Column(db.String(150))
    current_race = db.Column(db.Integer)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # lower case here !!
