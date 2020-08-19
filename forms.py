from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField
from wtforms.validators import InputRequired, Optional, Length, NumberRange, ValidationError


class SignupForm(FlaskForm):
    """Form for signing up a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class PlayerForm(FlaskForm):
    """Form for users to search for an NBA player"""
    first_name = StringField("Player First Name", validators=[InputRequired()])
    last_name = StringField("Player Last Name", validators=[InputRequired()])


class AdvancedForm(FlaskForm):
    """Form for advanced search for an NBA player stat"""
    first_name = StringField("Player First Name", validators=[InputRequired()])
    last_name = StringField("Player Last Name", validators=[InputRequired()])
    start_date = DateField("Starting Date", validators=[InputRequired()])
    end_date = DateField("End Date", validators=[InputRequired()])
    pts = IntegerField("Points", validators=[Optional(), NumberRange(
        min=0, message="Points must be greater or equal to 0!")])
    reb = IntegerField("Rebounds", validators=[
        Optional(), NumberRange(min=0, message="Rebounds must be greater or equal to 0!")])
    ast = IntegerField("Assists", validators=[
        Optional(), NumberRange(min=0, message="Assists must be greater or equal to 0!")])
    stl = IntegerField("Steals", validators=[
        Optional(), NumberRange(min=0, message="Steals must be greater or equal to 0!")])
    blk = IntegerField("Blocks", validators=[
        Optional(), NumberRange(min=0, message="Blocks must be greater or equal to 0!")])

    def validate_end_date(form, field):
        if field.data < form.start_date.data:
            raise ValidationError(
                "End date must not be earlier than start date.")
