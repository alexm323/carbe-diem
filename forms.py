from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField("username", validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField("password", validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    # email = StringField("email", validators=[InputRequired(), Email()])
    # first_name = StringField("first_name", validators=[InputRequired()])
    # last_name = StringField("last_name", validators=[InputRequired()])


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[
                        InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8, max=80)])


class TDEEForm(FlaskForm):
    gender = SelectField("Gender", choices=[
                         ("male", "Male"), ('female', 'Female')])
    height = IntegerField("Height (inches)", validators=[InputRequired()])
    weight = IntegerField("Weight (pounds)", validators=[InputRequired()])
    age = IntegerField("Age (years)", validators=[InputRequired()])
    activity_level = SelectField("Activity Level", choices=[('level1', 'Sedentary'), (
        'level2', 'Lightly Active'), ('level3', 'Moderately Active'), ('level4', 'Very Active'), ('level5', 'Extra Active')])


class FoodForm(FlaskForm):
    food = StringField("Food", validators=[
        InputRequired(), Length(max=50)])


class SelectFood(FlaskForm):
    selected_food = SelectField("Selected Food")
    servings = IntegerField("Servings")
