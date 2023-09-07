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
    """ Movie class representing the 'movies' table in the database.

    Attributes:
        id (int): The primary key for the movie record.
        title (str): The title of the movie.
        director (str): The director of the movie.
        year (str): The release year of the movie.
        rating (float): The movie's rating - same for all users.
        img (str): URL of the movie's image.
        imdbID (str): The IMDb ID of the movie.
        plot (str): The plot summary of the movie.
        notes (str): Additional notes about the movie - same for all users.
        recomend1 (str): IMDb ID of the first recommended movie.
        recomend2 (str): IMDb ID of the second recommended movie.
        recomend3 (str): IMDb ID of the third recommended movie.
        """
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

    @staticmethod
    def to_json(self):
        """Uses SerializedMixin to_dict() func to convert object to dict/json"""
        return self.to_dict()


class UserMovie(db.Model, SerializerMixin):
    """UserMovie class representing the 'user_movies' table in the database.

    Attributes:
        row_id (int): The primary key for the user movie record.
        user_id (int): The ID of the user associated with the movie.
        movie_id (int): The ID of the movie associated with the user.
        user_notes (str): Additional notes provided by the user for the movie.
        user_rating (float): The user's rating for the movie.
        """
    __tablename__ = "user_movies"
    row_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_data.user_id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"))
    user_notes = db.Column(db.String)
    user_rating = db.Column(db.Float)
    user = db.relationship('User', backref='user_movies', lazy=True)

    @staticmethod
    def to_json(self):
        """Uses SerializedMixin to_dict() func to convert object to dict/json"""
        return self.to_dict()


class User(db.Model, UserMixin):
    """User class representing the 'user_data' table in the database.

     Attributes:
         id (int): The primary key for the user record.
         username (str): The username of the user.
         email (str): The email address of the user.
         password (str): The hashed password of the user.

     Methods:
         get(user_id: str): Get a user by their ID.
         get_email(email: str): Get a user by their email address.
         add_user(name, email, password): Add a new user to the database.
     """
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
    """Review class representing the 'reviews' table in the database.

        Attributes:
            review_id (int): The primary key for the review record.
            user_id (int): The ID of the user who wrote the review.
            movie_id (int): The ID of the movie being reviewed.
            review_title (str): The title of the review.
            review_text (str): The content of the review.
            review_rating (float): The rating given in the review.
            review_date (str): The date when the review was created.

        Methods:
            __init__(self, user_id, movie_id, review_title, review_text, review_rating, review_date): Initialize a new review instance.
        """
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
