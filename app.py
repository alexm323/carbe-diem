from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db,  connect_db, User, Stats, Food, Entry
import requests
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from credentials import api_app_id, api_app_key
from forms import LoginForm, RegisterForm, TDEEForm, FoodForm, SelectFood
from werkzeug.security import generate_password_hash, check_password_hash
from tdee_calculator import *
import datetime
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
        login_user(new_user)
        return redirect('/metrics')
    return render_template('signup.html', form=form)


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect('/')
###########################################

###########################################
# Helper Functions


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


def food_in_database(food):
    previous_foods = Food.query.all()
    query_terms = []
    for query_food in previous_foods:
        query_terms.append(query_food.query_term)
    if food in query_terms:
        return True
    else:
        return False

#########################################################


@ app.route('/')
def home_page():
    """Display our landing page"""
    return render_template('landing.html')


# @ app.route('/contact')
# def contact_page():
#     return render_template("contact.html")


@ app.route('/dashboard')
@ login_required
def show_dashboard():
    if (len(current_user.statistics) == 0):
        return redirect('/metrics')

    u = User.query.get(current_user.id)
    entries = u.user_entries
    today = datetime.date.today()
    todays_entries = []
    for entry in entries:
        if entry.date == today:
            todays_entries.append(entry)
    sum_calories = 0
    sum_carbs = 0
    sum_fat = 0
    sum_protein = 0
    for entry in todays_entries:
        sum_calories = sum_calories + entry.food.calories
        sum_fat = sum_fat + entry.food.fat
        sum_carbs = sum_carbs + entry.food.carbs
        sum_protein = sum_protein + entry.food.protein
    return render_template('dashboard.html', user=current_user, entries=todays_entries, today=today, sum_calories=sum_calories, sum_carbs=sum_carbs, sum_fat=sum_fat, sum_protein=sum_protein)

#####################################################
# Total Daily Energy Expenditure Calculator


@ app.route('/metrics', methods=['GET', 'POST'])
@ login_required
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
    return render_template('metrics.html', form=form, user=current_user)

#####################################################


@ app.route('/search', methods=['GET', 'POST'])
def search_food_form():
    form = FoodForm()
    if form.validate_on_submit():
        food = request.form['food'].strip().lower()
        if food_in_database(food) == False:

            food_response = get_food_info(food)
            for item in food_response:
                calories = food_response[item]['kCal']
                fat = food_response[item]['Fats']
                carbs = food_response[item]['Carbs']
                protein = food_response[item]['Protein']
                new_food = Food(query_term=food, item=item,
                                calories=calories, fat=fat, carbs=carbs, protein=protein)
                db.session.add(new_food)
                db.session.commit()
            session['food'] = food
            # print(session['food'])
            return redirect('/new_entry')
        else:
            session['food'] = food
            # print(session['food'])
            return redirect('/new_entry')

    return render_template('foodSearch.html', form=form)


@ app.route('/new_entry', methods=['GET', 'POST'])
def submit_new_entry_form():
    form = SelectFood()
    query_term = session['food']

    foods = Food.query.filter_by(query_term=query_term).all()
    form.selected_food.choices = [(food.id, food.item) for food in foods]

    if form.validate_on_submit():

        food = request.form['selected_food']
        date = datetime.date.today().strftime("%m/%d/%y")
        user_id = current_user.id
        new_entry = Entry(food_id=food, date=date, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('newEntry.html', foods=foods, form=form)


@ app.route('/learn')
def show_learn_info():
    return render_template('learn.html')


# Need to add some if statements to the logic of the get food function so that if the food that is being searched matches a query term from the food table in the database then we just display the data we already have instead of searching again and making another api call


# check for specific food id so that there are no duplicates
# look at date not datetime objects
# if a user doesnt update their stats then we use the previous stats
# if a user updates their tdee then we take a measure on that date otherwise it stays the same
# is there a way to generate a tdee automatically each day?
# maybe i dont need to do that and I can just check for the date and if there is no entries I just show the normal graphs and tables and if
# the user has entries then I can show the subtracted values on the dashboard
