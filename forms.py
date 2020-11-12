from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    """Make the login form for a user, remember recalls if a user is in the session already"""
    username = StringField("username", validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField("password", validators=[
                             InputRequired(), Length(min=8, max=80)])
    # remembers the user in the current session
    # remember = BooleanField('remember me')
    # email = StringField("email", validators=[InputRequired(), Email()])
    # first_name = StringField("first_name", validators=[InputRequired()])
    # last_name = StringField("last_name", validators=[InputRequired()])


class RegisterForm(FlaskForm):
    """Registers a user, dont need to collect too much data here"""
    email = StringField("Email", validators=[
                        InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8, max=80)])


class TDEEForm(FlaskForm):
    """These are the users metrics and contain various pieces of information needed for health calculations"""
    gender = SelectField("Gender", choices=[
                         ("male", "Male"), ('female', 'Female')])
    height = IntegerField("Height (inches)", validators=[InputRequired()])
    weight = IntegerField("Weight (pounds)", validators=[InputRequired()])
    age = IntegerField("Age (years)", validators=[InputRequired()])
    activity_level = SelectField("Activity Level", choices=[('level1', 'Sedentary'), (
        'level2', 'Lightly Active'), ('level3', 'Moderately Active'), ('level4', 'Very Active'), ('level5', 'Extra Active')])


class FoodForm(FlaskForm):
    """Searchable food field"""
    food = StringField("Food", validators=[
        InputRequired(), Length(max=50)])


class SelectFood(FlaskForm):
    """Drop down menu for selectable foods that are populated based on whether it is on the quick add section or if they are going through the food search route to find a food that is not in the database"""
    selected_food = SelectField("Database Food")
    servings = SelectField("Servings", choices=[(1, 1), (
        2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])
