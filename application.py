import os
import requests
import hashlib
from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash
from flask_session import Session
from forms import RegistrationForm, LoginForm, SearchForm, ReviewForm
from flask_bcrypt import Bcrypt 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = '387b28b25302f3d780ed53706cdeed2e'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['FLASK_GOLDEN_READS_DB'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)



@app.route("/")
@app.route("/home")
def index():
    return render_template('home.html', title="Home")


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit() and request.method == 'POST':
        quest=form.search.data
        return books(quest)
    return render_template('search.html', title="Search", form=form)


@app.before_request
def make_session_permanent():
    session.permanent = True 


def get_google_books_data(isbn):
    fallback = "https://images.unsplash.com/photo-1499482125586-91609c0b5fd4?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=634&q=80"
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={isbn}&key=AIzaSyDTPZR0X5RS-Vb7k00pG9QfmykL-yTE514").json()
    items = response.get("items")
    rating = 0
    ratingsCount = 0
    pageNum = 0
    description = ""
    image_link = fallback

    if items:
        try:
            rating = items[0].get("volumeInfo").get("averageRating")
            ratingsCount = items[0].get("volumeInfo").get("ratingsCount")
            description = items[0].get("volumeInfo").get("description")
            pageNum = items[0].get("volumeInfo").get("pageCount")
            image_link = items[0].get("volumeInfo").get("imageLinks").get("thumbnail")
        except:
            rating = 0
            ratingsCount = 0
            pageNum = 0
            description = ""
            image_link = fallback
    
    return [pageNum, rating, description, image_link, ratingsCount]


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
        #session['user_img'] = db.execute("SELECT image_file FROM Users WHERE username=:username", {'username':username})
        #print(session['user_img'])
        if isbn:
            return redirect(url_for('books'))
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
            session['username'] = user.username
            session['user_img'] = user.image_file
            if isbn:
                return redirect(url_for("books",isbn=isbn))
            return redirect(url_for("search"))            
        else:
            return render_template('login.html',message="Wrong Email Address.") 
    return render_template('login.html', title="Login", form=form, next=isbn)


@app.route("/books", methods=['GET', 'POST'])
def books():
    form = SearchForm()
    result_images = []
    
    if form.validate_on_submit():
        quest = form.search.data
        if quest != None:
            quest = quest.strip().replace("'", "")
            result_books = db.execute("SELECT * from books where isbn LIKE ('%"+quest+"%')  or lower(title) LIKE lower('%"+quest+"%') or  lower(author) LIKE lower('%"+quest+"%') order by year desc;").fetchall()
            result_count = len(result_books)
            
            #image_link = ""
            for i in range(len(result_books)):
                image_link = get_google_books_data(result_books[i].isbn)[3]
                result_images.append(image_link)
            
                
            if result_count == 0:
                return render_template('books.html', form=form, title='404', quest=quest,result_count=result_count,message="404 Not Found"), 404

            return render_template('books.html', form=form , title='Search Results', quest=quest,result_count=result_count,result_books=result_books, result_images=result_images )
    return render_template('books.html', form=form)


@app.route("/book/<isbn>", methods=['GET', 'POST'])
def book(isbn):
    form = ReviewForm()
    message = None
    error = False
    is_reviewed = False
    fallback = "https://images.unsplash.com/photo-1499482125586-91609c0b5fd4?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=634&q=80"

    if request.method == 'POST' and session['logged_in']:
        my_rating = int(request.form.get('rating'))
        my_review = request.form.get('review')
        book_id = request.form.get('book_id')
        
        if my_review.strip() == "" or my_rating == "":
            message = "Invalid Review"
        else:
            db.execute("INSERT INTO review (username, review, rating, book_id) select :username,:review,:rating,:book_id where not exists (select * from review where username = :username and book_id = :book_id);",
            {
            'username': session['username'],
            'review': my_review,
            'rating': my_rating,
            'book_id':book_id
            })
            db.commit()
            is_reviewed = True
    res = db.execute("select * from books where isbn=:isbn;",{'isbn':isbn}).fetchone() 
    if res==None:
        return render_template('book.html')
    


    reviews = db.execute("select * from review where book_id=:id;",{'id':res.id}).fetchall()
    if request.method == "GET":
        try:
            if session['logged_in']:
                check_review = db.execute("select username from review where book_id=:id and username=:username;",
            {
                'id':res.id,
                'username': session['username']  
            }).fetchone()
                if check_review != None:
                    is_reviewed = True
        except:
            pass
    try:
        pageNum, rating, description, image_link, ratingsCount = get_google_books_data(isbn)
    except:
        error = True
        pageNum, rating, description, image_link, ratingsCount = 0, 0, "", fallback, 0
    
    return render_template('book.html',obj_book=res, form=form, pageNum=pageNum, description=description, image_link=image_link, rating=rating,ratingsCount=ratingsCount, reviews=reviews,message=message,is_reviewed=is_reviewed,error=error)
   

@app.route("/api/<isbn>")
def api_url(isbn):
    fallback = "https://images.unsplash.com/photo-1499482125586-91609c0b5fd4?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=634&q=80"
    res = db.execute("select * from books where isbn=:isbn;",{'isbn':isbn}).fetchone()
    if res == None:
        return jsonify({
            "error": "Invalid isbn.",
            "Message": "Error"
            }),404
    try:
        pageNum, rating, description, image_link, ratingsCount = get_google_books_data(isbn)
    except:
        pageNum, rating, description, image_link, ratingsCount = 0, 0, "", fallback, 0
    
    return jsonify({
        "title": res.title,
        "author": res.author,
        "year": res.year,
        "isbn": res.isbn,
        "pageCount":pageNum,
        "ratings_count": ratingsCount,
        "average_rating": rating,
        "description": description,
        "image_link": image_link
    }),200



@app.route("/logout")
def logout():
    
    session.clear()
    return redirect(url_for("login"))



get_google_books_data('1451648537')
if __name__ == '__main__':
    app.debug = True
    app.run()
