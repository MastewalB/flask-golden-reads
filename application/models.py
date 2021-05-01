from application import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}', '{self.image_file}')"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(120), unique=True, nullable=False)
    author = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', '{self.year}', '{self.isbn}')"



class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    review = db.Column(db.Text)
    rating = db.Column(db.Integer)
    date_reviewed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    def __repr__(self):
        return f"Review('{self.username}','{self.id}','{self.rating}')"