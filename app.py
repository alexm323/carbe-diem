from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db,  connect_db, User, Stats
import requests
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from credentials import api_app_id, api_app_key
from forms import LoginForm, RegisterForm, TDEEForm, FoodForm
from werkzeug.security import generate_password_hash, check_password_hash
from tdee_calculator import *
import json
from jsonpath_ng import jsonpath, parse
search_endpoint = 'https://api.edamam.com/api/food-database/v2/parser'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nutrientry'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "ILessThan3You"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

BASE = "https://api.edamam.com/api/food-database/v2/parser"
###########################################
# User Login Section
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('/dashboard')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New User created!</h1>'
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
###########################################


@ app.route('/')
def home_page():
    """Display our landing page"""
    return render_template('landing.html')


# @ app.route('/contact')
# def contact_page():
#     return render_template("contact.html")


@app.route('/dashboard')
@login_required
def show_dashboard():
    if (len(current_user.statistics) == 0):
        return redirect('/tdee')
    return render_template('dashboard.html', user=current_user)

#####################################################
# Total Daily Energy Expenditure Calculator


@app.route('/tdee', methods=['GET', 'POST'])
@login_required
def show_calculator_form():
    """Use a total daily energy expenditure to find and add the users current stats to their user stats information"""
    form = TDEEForm()
    if form.validate_on_submit():
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        age = request.form['age']
        activity_level = request.form['activity_level']
        tdee = calculate_tdee(gender, height, weight, age, activity_level)
        bmi = calculate_bmi(height, weight)
        ideal_weight = calculate_ideal_weight(height)
        pounds_to_lose = calculate_pounds_to_lose(weight, height)
        ideal_time_frame = calculate_ideal_time_frame(tdee, pounds_to_lose)
        if ((Stats.query.filter_by(user_id=current_user.id).first()) == None):
            new_stats = Stats(user_id=current_user.id,
                              height=height, weight=weight, tdee=tdee, bmi=bmi, ideal_weight=ideal_weight, pounds_to_lose=pounds_to_lose, ideal_time_frame=ideal_time_frame)
            db.session.add(new_stats)
            db.session.commit()
            return redirect('/dashboard')
        else:
            current_stats = Stats.query.filter_by(
                user_id=current_user.id).first()
            current_stats.height = height
            current_stats.weight = weight
            current_stats.tdee = tdee
            current_stats.bmi = bmi
            current_stats.ideal_weight = ideal_weight
            current_stats.pounds_to_lose = pounds_to_lose
            current_stats.ideal_time_frame = ideal_time_frame
            db.session.commit()
            return redirect('/dashboard')
    return render_template('tdee.html', form=form, user=current_user)

#####################################################


def get_food_info(food):
    food = food
    payload = {'app_id': api_app_id, 'app_key': api_app_key,
               'ingr': food, 'nutrition-type': 'logging', 'category': 'generic-meals'}
    search_result = requests.get(BASE, params=payload).json()
    food_arr = search_result['hints']
    food_dict = {}
    for index in food_arr:
        macro_dict = {}

        food_label = index['food']['label']
        macro_dict['kCal'] = round(index['food']['nutrients']['ENERC_KCAL'])
        macro_dict['Carbs'] = round(index['food']['nutrients']['CHOCDF'])
        macro_dict['Fats'] = round(index['food']['nutrients']['FAT'])
        macro_dict['Protein'] = round(index['food']['nutrients']['PROCNT'])
        food_dict[food_label] = macro_dict

    return food_dict

# @ app.route('/calories')
# def food_data():
#     response = get_food_info('taco')

#     return render_template('diary.html', response=response)


@app.route('/diary', methods=['GET', 'POST'])
def food_form():
    form = FoodForm()
    if form.validate_on_submit():
        food = request.form['food']
        food_response = get_food_info(food)

    return render_template('diaryForm.html', form=form)


# python background jobs
# database object with a time stamp that is 20 hours from now and each time the person logs in, check if they have one of those database objects with the time in the past. It wont be real time
# Things before mentor call, start working on the after form is submitted for the food diary, need to have an outline of what it should look like, dont know if I want to break it up in days or if it should be by section of the day. I want to generate a select field for a person to be able to submit their final choice of food for submission into the database.

@app.route('/learn')
def show_learn_info():
    return render_template('learn.html')
