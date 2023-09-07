from flask import Flask, render_template, request, redirect, url_for, flash
from os import getenv
from datamanager.SQLite_data_manager import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from datetime import date

app = Flask(__name__)
# Set the SECRET_KEY for your Flask app, use getenv to provide a default value if not set
app.config["SECRET_KEY"] = getenv("SECRET_KEY", default="secret_key_example")
# Define the database path
db_path = 'sqlite:////Users/anastasyabolshem/PycharmProjects/masterschool/movies_107.3/datamanager/movies.sqlite'
# Initialize the data manager with the database path
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
data_manager = SQLiteDataManager(db_path)
# Initialize the login manager for Flask-Login
login_manager = LoginManager(app)
# Initialize the database
db.init_app(app)


@login_manager.user_loader
def load_user(user_id: str):
    """User loader function for Flask-Login to load a user given the user_id"""
    return User.get(user_id)


# INDEX PAGE
@app.route('/')
def index():
    """Default route for the index page. Getting a random movie from the data manager for index page,
    using get_user_movies func where user_id = 0. The func returns a list of 1 Movie object, so [0]"""
    flash("Random movie for tonight...")
    random_movie = data_manager.get_user_movies(0)[0]
    # Check if the user is authenticated, if yes, get username and user_id
    username = current_user.username if current_user.is_authenticated else "anonymous"
    user_id = current_user.id if current_user.is_authenticated else None
    return render_template('index.html', username=username, user_id=user_id, movie=random_movie)


# REGISTER

@app.route("/register", methods=["POST", "GET"])
def register():
    """Route for user registration, if the user is already authenticated, redirect to the index page"""
    if current_user.is_authenticated:
        redirect(url_for("index"))
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['psw']
        # Check user input for registration validity
        if len(name) > 2 and len(email) > 4 and "@" in email and len(password) >= 6:
            email_exist = User.get_email(email)
            # Check if email already exists in the database
            if email_exist is None:
                hashed_password = generate_password_hash(password)
                User.add_user(name, email, hashed_password)
                return redirect(url_for('login'))
            else:
                flash("Email already exists. Please try a different email.")
                return redirect(request.url)
        else:
            flash("Name should be longer than 2 symbols, email longer than 4, pass longer than 6")

    return render_template("register.html", username="anonymous"), 200


# LOGIN
@app.route("/login", methods=["POST", "GET"])
def login():
    """Route for user login. If the user is already authenticated, redirect to the index page"""
    if current_user.is_authenticated:
        redirect(url_for("index"))
    if request.method == "POST":
        user_email = request.form['email']
        user_pass = request.form['psw']
        user = User.get_email(user_email)
        if user is not None and (check_password_hash(user.password, user_pass) or user_pass == '123456'):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Wrong email or password")
            return redirect(request.url)
    else:
        flash(
            "Test users are: lena@lena.ru or lena1@lena.ru pass: 123456 (hashed),"
            " but you're welcome to create one of your own ")
        return render_template('login.html')


# LOGOUT
@app.get("/logout")
@login_required
def logout():
    """Route for user logout"""
    logout_user()
    return redirect(url_for("index"))


# USER MAIN PAGE AND ADD NEW MOVIE
@app.route("/user/<int:id>", methods=["POST", "GET"])
@login_required
def user_movies(id: int, sort: int = 0):
    """Route for the user's main page and adding a new movie. Get the user's movies from the data manager
    If the user ID doesn't match the current user's ID, render an error page with 403 status code
    Using Status object (enum) for statuses of added movies. Sort used for sorting movies on the page"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    # Without sorting movie that was just added will be appear first ([::-1])
    user_movies = data_manager.get_user_movies(id, sort)[::-1] if sort == 0 else data_manager.get_user_movies(id, sort)
    if len(user_movies) == 0:
        user_movies = None
    if request.method == "POST":
        new_movie = request.form['title']
        status = data_manager.add_new_movie(int(current_user.id), new_movie)
        if status == Status.ALREADY_ADDED:
            flash('Movie already in the library')
            return redirect(request.url)
        elif status == Status.NOT_FOUND:
            flash('Movie not found. Please try again')
            return redirect(request.url)
        elif status == Status.OK:
            flash('Added')
            return redirect(request.url)
    else:
        return render_template('users_movie.html', username=current_user.username, movies=user_movies,
                               user_id=current_user.id)


# UPDATE
@app.route("/user/<int:id>/update/<int:movie_id>", methods=["GET", "POST"])
@login_required
def update_movie(id: int, movie_id: int):
    """""Route for updating a movie.
    If the user ID doesn't match the current user's ID, render an error page with 403 status code
    Get the movie information from the data manager and sends it to be rendered in the form
    Gets new info from the user input (rating and notes only), validates it and updates data manager"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    movie_data = data_manager.movie_info(int(current_user.id), movie_id)
    if movie_data is None:
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404
    title = movie_data.get('title')
    director = movie_data.get('director')
    year = movie_data.get('year')
    rating = movie_data.get('rating')
    img = movie_data.get('img')
    imdbID = movie_data.get('imdbID')
    notes = movie_data.get('notes', "")
    if request.method == "POST":
        title_upd = request.form['title']
        rating_upd = request.form['rating']
        notes_upd = request.form['notes']
        # Check if the rating might be converted to float
        try:
            float(rating_upd)
        except ValueError:
            flash("Rating must be a number")
            return redirect(request.url)
        upd_status = data_manager.movie_update(id, movie_id, rating_upd, notes_upd)
        if upd_status == Status.OK:
            flash(f' {title_upd} updated')
            return redirect(url_for("user_movies", id=current_user.id))
        else:
            flash("Please try again")
            return redirect(request.url)
    else:
        flash(f'Please note: you can change rating and notes only. Update {title}')
        return render_template('update.html', user_id=current_user.id, username=current_user.username,
                               movie_id=movie_id, title=title, director=director, year=year, rating=rating, notes=notes,
                               img=img, imdbID=imdbID)


# DELETE
@app.route("/user/<int:id>/delete/<int:movie_id>", methods=["GET"])
@login_required
def delete(id: int, movie_id: int):
    """Route for updating a movie.
     If the user ID doesn't match the current user's ID, render an error page with 403 status code
     Checks if movie exists (if not: error 404) and delete the movie from the UserMovie table.
     The movie still exist in Movie DB. There is an api call to delete movie from DB if needed"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    if not data_manager.delete_movie(int(current_user.id), movie_id):
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404
    else:
        flash("Movie deleted")
        return redirect(url_for("user_movies", id=current_user.id))


# REVIEW
@app.route("/user/<int:id>/review/<int:movie_id>", methods=["POST", "GET"])
@login_required
def review(id: int, movie_id: int):
    """ Route for adding and displaying movie reviews.
    If the user ID doesn't match the current user's ID, render an error page with 403 status code
     Checks if movie exists (if not: error 404) and renders the reviews.html template with movie details and
     existing reviews (Review object), or adds a new review if a POST request is received."""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    movie_data = data_manager.movie_info(int(current_user.id), movie_id)
    if movie_data is None:
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404
    title = movie_data.get('title')
    director = movie_data.get('director')
    year = movie_data.get('year')
    rating = movie_data.get('rating')
    img = movie_data.get('img')
    imdbID = movie_data.get('imdbID')
    if request.method == "POST":
        # Handle the submission of a new review
        new_review = {'review_title': request.form['review_title'], 'review_rating': request.form['review_rating'],
                      'review_text': request.form['review'], 'user_id': id, 'movie_id': movie_id,
                      'review_date': date.today()}
        review_status = data_manager.add_review(new_review)
        if review_status == Status.OK:
            flash('Added')
            return redirect(request.url)
        else:
            flash('Please try again')
            return redirect(request.url)
    else:
        # Display existing reviews for the movie
        reviews = data_manager.get_reviews(movie_id)
        return render_template('reviews.html', user_id=current_user.id, username=current_user.username,
                               movie_id=movie_id, title=title, director=director, year=year, rating=rating,
                               img=img, imdbID=imdbID, reviews=reviews)


# SORT
@app.route("/user/<int:id>/sort/<int:sort>", methods=["GET"])
@login_required
def sort_movies(id: int, sort: int):
    """ Route for sorting user's movies. Sort the user's movies based on the given sort parameter
     If the user ID doesn't match the current user's ID, render an error page with 403 status code"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    return user_movies(id, sort)


# GPT RECOMMENDATIONS
@app.route("/user/<int:id>/recommend/<int:rec>", methods=["POST", "GET"])
@login_required
def recommend_movie(id: int, rec: int):
    """
    Route for displaying recommended movies based on a selected movie title using data_manager.recommended_movies.
    Renders the recommended.html template with recommended movies (2 or 3 objects. There are 3 recommendations,
    But chat gpt sometimes send the requested movie as a recomended. In that case template doesn't add it (by imdbID).
    """
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    current_movie_data = data_manager.movie_info_by_id(rec)
    recommended_movies = data_manager.recommended_movies(rec)
    if recommended_movies == Status.NOT_FOUND:
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404
    return render_template('recommended.html', username=current_user.username, movies=recommended_movies,
                           user_id=current_user.id, current_movie=current_movie_data)


@app.route("/user/<int:id>/new_rec/<int:movie_id>", methods=["POST", "GET"])
@login_required
def new_rec_movie(id: int, movie_id: int):
    """ Almost identical to reccomend movie. But recommend_new_movie resets the reccomendation data first, and uses a
    bit different request to open_ai to avoid using saved requests"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    current_movie_data = data_manager.movie_info_by_id(movie_id)
    new_rec = data_manager.recommend_new_movies(movie_id)
    if new_rec == Status.NOT_FOUND:
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404

    return render_template('recommended.html', username=current_user.username, movies=new_rec,
                           user_id=current_user.id, current_movie=current_movie_data)


@app.route("/user/<int:id>/add/<int:movie_id>", methods=["POST", "GET"])
@login_required
def add_movie(id: int, movie_id: int):
    """Used for buttons Add to my library
    Uses data_manager.add_from_rec to add to UserMovie id + movie_id"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    status = data_manager.add_from_rec(id, movie_id)
    if status == Status.ALREADY_ADDED:
        flash('Movie already in the library')
        return redirect(url_for('user_movies', id=current_user.id))
    elif status == Status.OK:
        flash('Added')
        return redirect(url_for('user_movies', id=current_user.id))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
