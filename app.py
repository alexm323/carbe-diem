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
import os
search_endpoint = 'https://api.edamam.com/api/food-database/v2/parser'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql:///carbe_diem')
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
login_manager.login_view = "/register_and_login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route to display our login and register forms


@app.route('/register_and_login')
def register_and_login():
    """Renders the template for our login and register forms"""
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template('login_and_register.html', login_form=login_form, register_form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/dashboard')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
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
    else:
        return redirect('/register_and_login')
    # return render_template('login_and_register.html', form=form)


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect('/')
###########################################

###########################################
# Helper Functions


def get_food_info(food):
    """Send payload to api and parse through data based on the food chosen to be searched returns a food dictionary for every food that is gathered from a particular query"""
    food = food
    # Payload for food search where ingr is the ingredient we send to the api
    payload = {'app_id': api_app_id, 'app_key': api_app_key,
               'ingr': food, 'nutrition-type': 'logging', 'category': 'generic-meals'}\
        # return our search result as json
    search_result = requests.get(BASE, params=payload).json()
    # hints is a key in the response object
    food_arr = search_result['hints']
    # initialize an empty dictionary to set all of our food information
    food_dict = {}
    # cycle through and extract the data from the response object
    for index in food_arr:
        # set a default dictionary
        macro_dict = {'kCal': 0, 'Carbs': 0, 'Fats': 0, 'Protein': 0}
        # grab the name of the food
        food_label = index['food']['label']
        # rounding the food data to make it easier to understand, using .get method here because some items lack some of the given nutrients and it would break otherwise
        macro_dict['kCal'] = round(
            index['food']['nutrients'].get('ENERC_KCAL', 0))
        macro_dict['Carbs'] = round(
            index['food']['nutrients'].get('CHOCDF', 0))
        macro_dict['Fats'] = round(index['food']['nutrients'].get('FAT', 0))
        macro_dict['Protein'] = round(
            index['food']['nutrients'].get('PROCNT', 0))
        # sets our food dictionary data
        food_dict[food_label] = macro_dict
    # return our now full food dictionary
    return food_dict


def food_in_database(food):
    """ check if a food has been searched for before to retrieve data from our database instead of making an additional api call returns a boolean value"""
    # gather all the foods
    previous_foods = Food.query.all()
    # initalize an empty array to keep track of the query terms which is the name a user has searched by
    query_terms = []
    # cycle through previous foods
    for query_food in previous_foods:
        # we only want the query column here
        query_terms.append(query_food.query_term)
    # check if the food we have searched for is in the database already and return true or false based on that result
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

#########################################################
#########################################################
#########################################################
# Our dashboard contains most of the primary functions of our application

@ app.route('/dashboard')
@ login_required
def show_dashboard():
    """Show the dashboard and generate 3 forms as well as our user data and charts. Can only be reached once a user inputs their metrics"""
    # load in our 3 forms
    food_form = FoodForm()
    metrics_form = TDEEForm()
    select_food_form = SelectFood()
    # display and sort the foods for a user to select
    all_foods = Food.query.order_by(Food.item).all()
    # Need to use a list comprehension to pass in data to our select form from our forms.py
    select_food_form.selected_food.choices = [
        (food.id, food.item) for food in all_foods]
    # Check if a user currently has metrics data , if not then take them to the metrics page to input data
    if (len(current_user.statistics) == 0):
        return redirect('/metrics')
    # get user data from our current users id
    u = User.query.get(current_user.id)
    # check for a users food entries for the data
    entries = u.user_entries
    # initialize the data for the current day
    today = datetime.date.today()
    # initialize an empty list to check only todays entries
    todays_entries = []
    # cycle through the data and grab only the entries that are on the current day
    for entry in entries:
        if entry.date == today:
            todays_entries.append(entry)
    # Need to set these values so that there is a default
    sum_calories = 0
    sum_carbs = 0
    sum_fat = 0
    sum_protein = 0
    # cycle through the entries for today and add up the totals factoring in the number of servings
    for entry in todays_entries:
        sum_calories = (sum_calories + (entry.food.calories*entry.servings))
        sum_fat = (sum_fat + (entry.food.fat*entry.servings))
        sum_carbs = (sum_carbs + (entry.food.carbs*entry.servings))
        sum_protein = (sum_protein + (entry.food.protein*entry.servings))
    # return and pass in the dashboard template with all of the form data and food data for the sums and metrics
    return render_template('dashboard.html', select_food_form=select_food_form, metrics_form=metrics_form, food_form=food_form, user=current_user, entries=todays_entries, today=today, sum_calories=sum_calories, sum_carbs=sum_carbs, sum_fat=sum_fat, sum_protein=sum_protein)

#####################################################
# Our initial metrics form


@ app.route('/metrics', methods=['GET', 'POST'])
@ login_required
def show_calculator_form():
    """Use a total daily energy expenditure to find and add the users current stats to their user stats.
    Information for the calculator itself can be seen in tdee_calculator.py, has more than tdee and we pass in all that information to the database for a user """
    form = TDEEForm()
    # once the user fills out and completes this form they will have access to our dashboard
    if form.validate_on_submit():
        # process the form data
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        age = request.form['age']
        activity_level = request.form['activity_level']
        # run the calculations for the various health metrics
        tdee = calculate_tdee(gender, height, weight, age, activity_level)
        bmi = calculate_bmi(height, weight)
        ideal_weight = calculate_ideal_weight(height)
        pounds_to_lose = calculate_pounds_to_lose(weight, height)
        ideal_time_frame = calculate_ideal_time_frame(tdee, pounds_to_lose)
        # check if the user currently has stats, if they dont then we make a new stats entry to our database and give access to the database
        if ((Stats.query.filter_by(user_id=current_user.id).first()) == None):
            new_stats = Stats(user_id=current_user.id,
                              height=height, weight=weight, tdee=tdee, bmi=bmi, ideal_weight=ideal_weight, pounds_to_lose=pounds_to_lose, ideal_time_frame=ideal_time_frame)
            db.session.add(new_stats)
            db.session.commit()
            return redirect('/dashboard')
        # else we will be just updating the current user stats and send them back to the dashboard and load in the updated info
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
    # Ideally the user will only have to visit this form once since it now lives on the dashbaord for easier access
    return render_template('metrics.html', form=form, user=current_user)

#########################################################
#########################################################
#########################################################
# Our food search section, no longer needs to generate a template since it exists in our dashboard now for ease of access


@ app.route('/search', methods=['GET', 'POST'])
@login_required
def search_food_form():
    """This processes our food search and will most likely become just a POST route to process data"""
    form = FoodForm()

    if form.validate_on_submit():
        # strip white space and get lowercase so search query is based only on content of letters
        food = request.form['food'].strip().lower()
        # use our helper function to check if the food has already been searched before. if it hasnt then we send an api call
        if food_in_database(food) == False:
            # send an api call using our function from the api
            food_response = get_food_info(food)
            # cycle through the names in the food response and we add all of the info for the searched food to our database
            for item in food_response:
                calories = food_response[item]['kCal']
                fat = food_response[item]['Fats']
                carbs = food_response[item]['Carbs']
                protein = food_response[item]['Protein']
                new_food = Food(query_term=food, item=item,
                                calories=calories, fat=fat, carbs=carbs, protein=protein)
                db.session.add(new_food)
                db.session.commit()
            # use the session object to remember the searched food to display to a user on the entry page
            session['food'] = food
            # Take them to the next screen where a user can confirm their entry
            return redirect('/new_entry')
        else:
            # if the food is already in the database then we just make that the new session item we are tracking so we can display the right info
            session['food'] = food
            # print(session['food'])
            return redirect('/new_entry')
    # probably deprecated now but im leaving it in for the time being
    return render_template('foodSearch.html', form=form)
#########################################################
#########################################################
#########################################################
# Allow a user to pass in a new entry to the database


@ app.route('/new_entry', methods=['GET', 'POST'])
@login_required
def submit_new_entry_form():
    """Allow a user see all of a foods information that we are parsing from the api and give them a drop down to select both the right item and a serving size"""
    form = SelectFood()
    # use the session object to track what the last searched food was

    query_term = session['food']
    # We get the foods that the user has searched and display them in alphabetical order
    foods = Food.query.filter_by(
        query_term=query_term).order_by(Food.item.asc()).all()
    # use a list comprehension to insert our choices into the selectfield from wtforms
    form.selected_food.choices = [(food.id, food.item) for food in foods]
    # this creates our entry in the database
    if form.validate_on_submit():

        food = request.form['selected_food']
        servings = request.form['servings']
        date = datetime.date.today().strftime("%m/%d/%y")
        user_id = current_user.id
        new_entry = Entry(food_id=food, date=date,
                          user_id=user_id, servings=servings)
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/dashboard')
    # still showing this page so a user can see the food data for all of the entries
    return render_template('newEntry.html', foods=foods, form=form)

#########################################################

# I was running into a bug where the food kept loading from the last search on the quick add section
# I decided a good work around was to reuse most of the code as a post route only and this takes care of the quick add feature without
# breaking because of the session['food'] query. A .get method wasnt working because it would return empty or id have to give it a default value and that wasn't achieving the functionality I wanted


@ app.route('/quick_add', methods=['POST'])
@login_required
def submit_quick_add_form():
    """Allows a user to quickly add an entry from existing database entries"""
    form = SelectFood()
    food = request.form['selected_food']
    servings = request.form['servings']
    date = datetime.date.today().strftime("%m/%d/%y")
    user_id = current_user.id
    new_entry = Entry(food_id=food, date=date,
                      user_id=user_id, servings=servings)
    db.session.add(new_entry)
    db.session.commit()
    return redirect('/dashboard')
    # still showing this page so a user can see the food data for all of the entries
#################################################################


@app.route('/remove_entry', methods=['POST'])
@login_required
def delete_entry():
    """User is able to delete their entries"""
    entry_id = request.form['entry_id']
    Entry.query.filter_by(id=entry_id).delete()
    db.session.commit()
    return redirect('/dashboard')
################################################################
# Havent worked on this in a while but i would like to expand it to include different information for different diets


@ app.route('/learn')
def show_learn_info():
    """There is a learning page specifically about intermittent fasting and at this time i have not added additional information"""
    return render_template('learn.html')


#########################################################
# Need to add some if statements to the logic of the get food function so that if the food that is being searched matches a query term from the food table in the database then we just display the data we already have instead of searching again and making another api call


# check for specific food id so that there are no duplicates
# look at date not datetime objects
# if a user doesnt update their stats then we use the previous stats
# if a user updates their tdee then we take a measure on that date otherwise it stays the same
# is there a way to generate a tdee automatically each day?
# maybe i dont need to do that and I can just check for the date and if there is no entries I just show the normal graphs and tables and if
# the user has entries then I can show the subtracted values on the dashboard
# <!-- Alex.onBoarding where the first thing would be a string with ('health info entered'), searched for a food, if it has been searched  , cards for responsive view of the dashboar
