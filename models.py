from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    statistics = db.relationship('Stats', backref='user')


class Stats(db.Model):
    __tablename__ = 'stats'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    tdee = db.Column(db.Integer)
    bmi = db.Column(db.Integer)
    ideal_weight = db.Column(db.Integer)
    pounds_to_lose = db.Column(db.Integer)
    ideal_time_frame = db.Column(db.Integer)


class Food(db.Model):
    __table__name = 'foods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_term = db.Column(db.String)
    item = db.Column(db.String, unique=True)
    calories = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    protein = db.Column(db.Integer)
# class CalorieDiary(db.model):
# For the object that I have to loop through the data and I can pull out the data that I need if I check against the search query already existing
# there are mem-storage objects that behave like databases "redis" "memcached"<-- Google this


class Entry(db.Model):
    __table__name = 'entries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='user_entries')
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    food = db.relationship('Food', backref='food_entries')
    date_id = db.Column(db.Integer, db.ForeignKey('dates.id'))
    date = db.relationship('Date', backref='date_entries')


class Date(db.Model):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    # entries = db.relationship('Entry', backref='date')
