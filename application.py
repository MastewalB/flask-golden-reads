import os
import requests
import hashlib
from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash
from flask_session import Session
from flask_login import LoginManager, current_user, login_user, login_required,logout_user
from forms import RegistrationForm, LoginForm, SearchForm
from flask_bcrypt import Bcrypt 
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
bcrypt = Bcrypt(app)

@app.route("/")
@app.route("/home")
def index():
    return render_template('home.html')


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    return render_template('search.html', title="Search", form=form)


@app.before_request
def make_session_permanent():
    session.permanent = True 


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
    
    isbn = request.args.get('next')
    form = RegistrationForm()
    if form.validate_on_submit() and request.method == 'POST':
        
        
        username = form.username.data
        email = form.email.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = db.execute("INSERT INTO Users (username, email, password) VALUES (:username, :email, :password);", {'username':username, 'email': email, 'password' :hashed_password})
        db.commit()
        session['logged_in'] = True
        session['username'] = username
        session['user_img'] = db.execute("SELECT image_file FROM Users WHERE username=:username", {'username':username})
        #print("Imageeeeeeee   ********* " + session['user_img'])
        if isbn:
            return redirect(url_for('book'))
        flash(f'Account successfully created for {form.username.data}!!', 'success')
        return redirect(url_for('search'))
        
    return render_template('signup.html', title='Sign Up', form=form, next=isbn)



@app.route("/login",methods=['GET','POST'])
def login():
    isbn = request.args.get('next')
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        user = db.execute("SELECT * FROM Users WHERE email=:email;", {'email':email}).fetchone()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['logged_in'] = True
            session['username'] = request.form.get('username')
            if request.form.get('remember'):
                make_session_permanent()
            if isbn:
                return redirect(url_for("book",isbn=isbn))
            return redirect(url_for("search"))            
        else:
            return render_template('login.html',message="Wrong Email Address.") 
    return render_template('login.html', title="Login", form=form, next=isbn)


@app.route("/book", methods=['GET', 'POST'])
def book():
    return render_template('book.html')


@app.route("/logout")
def logout():
    
    session.clear()
    return redirect(url_for("login"))



get_google_books_data(9781632168146)
if __name__ == '__main__':
    app.debug = True
    app.run()
