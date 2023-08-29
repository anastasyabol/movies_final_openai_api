from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Create a Flask app instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "sqlite:////Users/anastasyabolshem/PycharmProjects/masterschool/movies_107.3/datamanager/movies.sqlite"
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy()
db.init_app(app)


class Movie(db.Model):
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
    user_movies = db.relationship('UserMovie', backref='movie', lazy=True)


class UserMovie(db.Model):
    __tablename__ = "user_movies"
    row_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_data.user_id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"))
    user_notes = db.Column(db.String)
    user_rating = db.Column(db.Float)
    user = db.relationship('User', backref='user_movies', lazy=True)


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



with app.app_context():
    pass
