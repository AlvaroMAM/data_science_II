from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import user, airline, airport

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class UpdateProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class ChooseFavoritesForm(FlaskForm):
    favourites_airlines = SelectMultipleField('Favourite Airlines', choices=[(a.iata_code, a.airline) for a in airline.Airline.get_all_airlines()])
    favourites_airports = SelectMultipleField('Favourite Airports', choices=[(a.iata_code, a.airport) for a in airport.Airport.get_all_airports()])
    submit = SubmitField('Update Favorites')

class HomeForm(FlaskForm):
    submit = SubmitField('Find')