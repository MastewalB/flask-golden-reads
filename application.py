import os
import requests
import hashlib
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from flask_login import current_user, login_user, login_required,logout_user
from forms import RegistrationForm, LoginForm

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = '387b28b25302f3d780ed53706cdeed2e'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@app.route("/home")
def index():
    return render_template('home.html')


def password_hash(password):
    salt = "27a0091dee99016f8fb6599da096feff"
    salt_password = password + salt
    hashed_password = hashlib.md5(salt_password.encode())
    return hashed_password.hexdigest()


def get_google_books_data(isbn):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={isbn}&key=AIzaSyDTPZR0X5RS-Vb7k00pG9QfmykL-yTE514")
    value = response.json()
    #print(value)



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    
    form = RegistrationForm()
    return render_template('signup.html', title='Sign Up', form=form)



@app.route("/login",methods=['GET','POST'])
def login():

    form = LoginForm()
    return render_template('login.html', title="Login", form=form)






get_google_books_data(9781632168146)
if __name__ == '__main__':
    app.debug = True
    app.run()
