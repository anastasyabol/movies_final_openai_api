from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
import json

# Create a Flask app instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "sqlite:////Users/anastasyabolshem/PycharmProjects/masterschool/movies_107.3/datamanager/movies.sqlite"
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy()
db.init_app(app)


class Movie(db.Model, SerializerMixin):
    __tablename__ = "movies"
    id = db.Column('movie_id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    director = db.Column(db.String)
    year = db.Column(db.String)
    rating = db.Column(db.Float)
    img = db.Column(db.String)
    imdbID = db.Column(db.String)
    plot = db.Column(db.String)
    notes = db.Column(db.String)
    recomend1 = db.Column(db.String)
    recomend2 = db.Column(db.String)
    recomend3 = db.Column(db.String)
    user_movies = db.relationship('UserMovie', backref='movie', lazy=True)

    # def __init__(self, title, director, year, rating, img, imdbID, plot, notes, recomend1, recomend2, recomend3):
    #     self.title = title
    #     self.director = director
    #     self.year = year
    #     self.rating = rating
    #     self.img = img
    #     self.imdbID = imdbID
    #     self.plot = plot
    #     self.notes = notes
    #     self.recomend1 = recomend1
    #     self.recomend2 = recomend2
    #     self.recomend3 = recomend3
    #
    # def __dict__(self):
    #     return {
    #         'id': self.id,
    #         'title': self.title,
    #         'director': self.director,
    #         'year': self.year,
    #         'rating': self.rating,
    #         'img': self.img,
    #         'imdbID': self.imdbID,
    #         'plot': self.plot,
    #         'notes': self.notes,
    #         'recomend1': self.recomend1,
    #         'recomend2': self.recomend2,
    #         'recomend3': self.recomend3
    #     }
    #
    @staticmethod
    def to_json(self):
        return self.to_dict()


class UserMovie(db.Model, SerializerMixin):
    __tablename__ = "user_movies"
    row_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_data.user_id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"))
    user_notes = db.Column(db.String)
    user_rating = db.Column(db.Float)
    user = db.relationship('User', backref='user_movies', lazy=True)

    @staticmethod
    def to_json(self):
        return self.to_dict()


class User(db.Model, UserMixin):
    __tablename__ = "user_data"
    id = db.Column('user_id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self) -> str:
        """Self representation for print of the object"""
        return f"<Id: {self.id}, Username: {self.username}, Email: {self.email}>"

    @staticmethod
    def get(user_id: str):
        return User.query.get(int(user_id))

    def get_email(email: str):
        query = User.query.filter_by(email=email).first()
        print(query)
        return query if query is not None else None

    def add_user(name, email, password):
        new_user = User(username=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()


class Review(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_data.user_id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"))
    review_title = db.Column(db.String)
    review_text = db.Column(db.Text)
    review_rating = db.Column(db.Float)
    review_date = db.Column(db.Date)

    def __init__(self, user_id, movie_id, review_title, review_text, review_rating, review_date):
        self.user_id = user_id
        self.movie_id = movie_id
        self.review_title = review_title
        self.review_text = review_text
        self.review_rating = review_rating
        self.review_date = review_date
