from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                                validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = db.execute("SELECT * FROM Users WHERE username=:username;", {'username':username.data}).fetchone()
        if user:
            raise ValidationError('Username Already Taken. Please Choose a different one.')
    

    def validate_email(self, email):
        email = db.execute("SELECT * FROM Users WHERE email=:email;", {'email':email.data}).fetchone()
        if email:
            raise ValidationError('Email Already Taken. Please enter a different one.')

class LoginForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    search = StringField('Search and browse books', validators=[DataRequired()], render_kw={"placeholder": "Title / Author / ISBN"})
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    review = TextAreaField('Review', validators=[DataRequired()], render_kw={"placeholder": "Write Your Review here"})
    submit = SubmitField('Submit')

from application import db