from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# initialize the db
db = SQLAlchemy()

# Connect our db this is just boilerplate for using SQL Alchemy


def connect_db(app):
    db.app = app
    db.init_app(app)

# user class for our database


class User(UserMixin, db.Model):
    """Table for our users, we have a link to the statistics for a user so we can access them"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    statistics = db.relationship('Stats', backref='user')


class Stats(db.Model):
    """our user statistics that tracks all of the calculated data and is updated by the user if they submit a new metrics form"""
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
    """Tracking our food and this is extracted from the user searches once the api request is sent"""
    __table__name = 'foods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_term = db.Column(db.String)
    item = db.Column(db.String)
    calories = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    protein = db.Column(db.Integer)


class Entry(db.Model):
    """contains the data with a users entries. Gives us access to a user so we can see a users entries or sort entries by user, 
    the entry also keeps track of a serving as well as the date since we are tracking for today"""
    __table__name = 'entries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='user_entries')

    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    food = db.relationship('Food', backref='food_entries')

    date = db.Column(db.Date)
    servings = db.Column(db.Integer)
