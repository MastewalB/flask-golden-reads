import os
import requests
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
def index():
    return render_template('base.html')

def get_google_books_data(isbn):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={isbn}&key=AIzaSyDTPZR0X5RS-Vb7k00pG9QfmykL-yTE514")
    value = response.json()
    #print(value)


@app.route("/login",methods=['GET','POST'])
def login():
    isbn = request.args.get('next')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.execute("select * from users where username=:username and password=:password;",{'username':username,'password':password_hash(password)})
        if user.rowcount == 0:
            return render_template('login.html',message="Wrong Username or Password.")
        session['logged_in'] = True
        session['username'] = request.form['username']
        if isbn:
            return redirect(url_for("book",isbn=isbn))
        return redirect(url_for("search"))

    return render_template('login.html',next=isbn)



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    isbn = request.args.get('next')
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1!=password2:
            return render_template('signup.html',message="Password does not match.")
           
        try:
            password = password_hash(password1)
            user = db.execute("insert into users (username,password) values(:username ,:password);",{'username':username,'password':password})
            db.commit()
            session['logged_in'] = True
            session['username'] = username
            if isbn:
                return redirect(url_for("book",isbn=isbn))
            return redirect(url_for("search"))
        except:
            return render_template('signup.html',message="Username Already Exists.")
    return render_template('signup.html',next=isbn)


get_google_books_data(9781632168146)
if __name__ == '__main__':
    app.debug = True
    app.run()
