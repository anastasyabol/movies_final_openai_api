from sqlalchemy import create_engine, update, func
from sqlalchemy.orm import sessionmaker
from datamanager.data_manager_interface import DataManagerInterface, Status
from datamanager.database import *
from datamanager.omdb_url import omdb_url
import requests
from datamanager.gpt import gpt_recomendation, gpt_recomendation_new


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, file_path):
        """Initializes the SQLiteDataManager with a database file path."""
        self.engine = create_engine(file_path)
        self.Session = sessionmaker(bind=self.engine)

    def get_user_movies(self, user_id: int, sort: int = 0):
        """Get the movies for a specific user, sorted based on the given sort parameter. Returns list of dictionaries
        Returns list of Movie objects"""
        session = self.Session()
        result = []
        if user_id == 0:
            result = [Movie.query.order_by(func.random()).first()]
        else:
            query = session.query(Movie, UserMovie.user_rating, UserMovie.user_notes).join(
                UserMovie, Movie.id == UserMovie.movie_id).filter(UserMovie.user_id == user_id)

            if sort == 1:
                query = query.order_by(Movie.year)
            elif sort == 2:
                query = query.order_by(Movie.rating.desc())
            elif sort == 3:
                query = query.order_by(Movie.rating)
            elif sort == 4:
                query = query.order_by(Movie.title)

            user_movies = query.all()
            for movie, user_rating, user_notes in user_movies:
                if user_rating is not None:
                    movie.rating = user_rating
                if user_notes is not None:
                    movie.notes = user_notes
                result.append(movie)
        return result

    def add_new_movie(self, user_id: int, new_movie: str):
        """
        Add a new movie to a user's collection or the general Movie table if it doesn't exist.
        UserMovie object requires onlu user_id + movie_id
        Returns: Status (Enum object): The status of the operation (ALREADY_ADDED, OK, NOT_FOUND).
        """
        session = self.Session()

        # Check if the movie exists in the user's movies
        user_movie_query = session.query(UserMovie).filter_by(user_id=user_id)
        user_movie_query = user_movie_query.join(Movie, Movie.id == UserMovie.movie_id)
        user_movie_query = user_movie_query.filter(Movie.title == new_movie)

        user_movie = user_movie_query.first()
        if user_movie:
            session.close()
            return Status.ALREADY_ADDED

        # If not found in user's movies, check in the general Movie table
        movie_query = session.query(Movie).filter_by(title=new_movie)
        movie = movie_query.first()

        if movie:
            # Add the movie to the user's movies
            user_movie = UserMovie(user_id=user_id, movie_id=movie.id)
            session.add(user_movie)
            session.commit()
            session.close()
            return Status.OK
        else:
            return self.add_new_movie_to_db(new_movie, user_id)

        session.close()
        return Status.NOT_FOUND

    def add_from_rec(self, user_id: int, movie_id: int):
        """
        Add a movie that exist in db but not in UserMovie. (From Random Movie page or from Recommended movies)
        user_id (int): The ID of the user. movie_id (int): The ID of movie already in db.
        Returns: Status (Enum Object)The status of the operation (ALREADY_ADDED, OK).
        """
        session = self.Session()
        query = session.query(UserMovie).filter_by(movie_id=movie_id).first()
        if query:
            return Status.ALREADY_ADDED
        else:
            user_movie = UserMovie(user_id=user_id, movie_id=movie_id)
            session.add(user_movie)
            session.commit()
            session.close()
            return Status.OK

    def delete_from_db(self, movie_id):
        """
        Delete a movie from the database. FOR API USE ONLY
        Returns bool: True if the movie is deleted, False otherwise.
        PLEASE NOTE: The assumption here that there is no users with the requested movie.
        """
        session = self.Session()
        query = session.query(Movie).filter(Movie.id == movie_id)

        # Attempt to get the row
        row = query.one_or_none()

        if row:
            # Delete the row and return True
            session.delete(row)
            session.commit()
            return True
        else:
            # Return False if the row doesn't exist
            return False

    def add_new_movie_to_db(self, new_movie_title, user_id=0, imdbID=None):
        """Add a new movie to the Movie table in the database.
        new_movie_title (str): The title of the new movie.
        user_id (int): The ID of the user (default is 0).
        imdbID (str): The IMDb ID of the movie (default is None). Adding movies by imdbID used for recommendations
        by openai.
        Returns: Status (Enum Object): The status of the operation (OK or NOT_FOUND).
                """
        session = self.Session()
        url = omdb_url + "t="
        request = requests.post(url + new_movie_title + "&plot=full")
        # different url request for title/imdbID
        if imdbID is not None:
            url = omdb_url + "i="
            request = requests.post(url + imdbID + "&plot=full")
        api_data = request.json()
        if "Error" in api_data:
            return Status.NOT_FOUND
        # some movies returned with no rating
        try:
            rating = float(api_data['imdbRating'])
            notes = None
        except:
            rating = 7.77
            notes = "Please note: raiting wasn't availible, 7.77 added authomatically"

        new_movie = Movie(
            title=api_data['Title'],
            director=api_data['Director'],
            year=api_data['Year'],
            img=api_data['Poster'],
            imdbID=api_data['imdbID'],
            plot=api_data['Plot'],
            rating=rating,
            notes=notes)
        # In case of image not availible - not availible image is added
        if new_movie.img == "N/A":
            new_movie.img = 'https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg'
        session.add(new_movie)
        session.flush()
        # If func comes from user, so immediatly added to UserMovies
        if user_id != 0:
            user_movie = UserMovie(user_id=user_id, movie_id=new_movie.id)
            session.add(user_movie)
        session.commit()
        session.close()
        return Status.OK

    def movie_info(self, user_id: int, movie_id: int):
        """Get the information of a specific movie for a user.
        Overwriting rating and notes if user updated them
        Returns: A dictionary containing movie information.
        """
        session = self.Session()
        query = session.query(Movie, UserMovie.user_rating, UserMovie.user_notes).join(
            UserMovie, Movie.id == UserMovie.movie_id).filter(
            UserMovie.user_id == user_id, Movie.id == movie_id).first()

        if query:
            movie, user_rating, user_notes = query
            movie_info = vars(movie)
            if user_rating is not None:
                movie_info['rating'] = user_rating
            if user_notes is not None:
                movie_info['notes'] = user_notes
            session.close()
            print("********")
            print(movie_info)
            print(type(movie_info))
            return movie_info
        else:
            return None

    def movie_info_by_id(self, movie_id: int):
        """Get the information of a specific movie.
        Returns: A dictionary containing movie information.
        """
        session = self.Session()
        query = session.query(Movie).filter(Movie.id == movie_id).first()

        if query:
            movie_info = vars(query)
            session.close()
            return movie_info
        else:
            return None

    def movie_update(self, user_id: int, movie_id: int, rating_upd: str, notes_upd: str):
        """ Update a movie's user rating and notes.

        Args:
            user_id (int): The user's ID.
            movie_id (int): The ID of the movie to update.
            rating_upd (str): The updated user rating.
            notes_upd (str): The updated user notes.
        """
        session = self.Session()
        update_query = update(UserMovie).where(
            (UserMovie.movie_id == movie_id) & (UserMovie.user_id == user_id)
        ).values(user_rating=rating_upd, user_notes=notes_upd)
        session.execute(update_query)
        session.commit()
        session.close()
        return Status.OK

    def delete_movie(self, user_id: int, movie_id: int):
        """Delete a movie from UserMovies.
        Returns bool: True if the movie was deleted, False if it was not found.
        DOESN"T delete the movie from DB"""
        session = self.Session()
        query = session.query(UserMovie).filter(
            (UserMovie.movie_id == movie_id) & (UserMovie.user_id == user_id))

        # Attempt to get the row
        row = query.one_or_none()

        if row:
            # Delete the row and return True
            session.delete(row)
            session.commit()
            return True
        else:
            # Return False if the row doesn't exist
            return False

    def get_reviews(self, movie_id: int):
        """Get reviews for a specific movie by id
        Returns: A list of dictionaries representing reviews."""
        session = self.Session()
        query = session.query(Review, Movie, User.username).join(
            Movie, Movie.id == Review.movie_id).join(
            User, User.id == Review.user_id).filter(Review.movie_id == movie_id).order_by(
            Review.review_date.desc()).all()

        reviews_by_movie = []
        for review, movie_data, username in query:
            review_dict = vars(review)
            review_dict['username'] = username
            reviews_by_movie.append(review_dict)
        return reviews_by_movie

    def add_review(self, new_review_dict):
        """Add a new review to the database (Review object).
         Args: new_review_dict (dict): A dictionary containing review information.
         ** Makes an object from a dict
         Returns status.OK """
        session = self.Session()
        new_review = Review(**new_review_dict)
        session.add(new_review)
        session.commit()
        return Status.OK

    def movie_by_imdbID(self, imdbID):
        """Check if a movie with a given IMDb ID exists in the database and add it if not using add_new_movie_to_db
        (by imdbID).
        Returns: Status (Enum Object): A status indicating whether the movie was found or added successfully."""
        session = self.Session()
        movie_query = session.query(Movie).filter_by(imdbID=imdbID)
        movie = movie_query.first()
        if movie:
            return Status.OK
        else:
            if self.add_new_movie_to_db("", user_id=0, imdbID=imdbID) == Status.OK:
                return Status.OK
            else:
                return Status.NOT_FOUND

    def _update_recommendations(self, movie, recommend_function):
        """ Update movie recommendations using the specified recommendation function
        Args:
            movie: The movie for which recommendations should be updated.
            recommend_function: The recommendation function to use (recommend_movies / recommend_new_movies)..
            This private method updates the recommendations for the given movie using the provided recommendation function.
            It sets the movie's 'recomend1', 'recomend2', and 'recomend3' attributes with recommended movie IMDb IDs.

            """
        rec1, rec2, rec3 = recommend_function(movie.title)
        movie.recomend1 = rec1
        movie.recomend2 = rec2
        movie.recomend3 = rec3

    def _get_movie_statuses(self, imdb_ids):
        """Get the status of movies with the given IMDb IDs in the database.
        (If a reccomnded movie is in the db)
        Args:
            imdb_ids: A list of IMDb IDs to check.
        Returns list: A list of Status values indicating the status of each movie.
            """
        statuses = [self.movie_by_imdbID(imdb_id) for imdb_id in imdb_ids]
        return statuses

    def recommended_movies(self, movie_id):
        """
        Get recommended movies based on a selected movie (using chat-gpt - gpt function).
        Args: movie_id (int): The ID of the selected movie.
        Returns list of dictionaries representing recommended movies.

        This method retrieves recommended movies for a given movie by first checking if the movie has existing recommendations
        ('recomend1', 'recomend2', 'recomend3'). If any of the recommendations are missing, it updates them using the 'gpt_recomendation'
        function and commits the changes to the database.

        It then checks the status of recommended movies in the database using '_get_movie_statuses' and returns the data for the recommended
        movies if all have a status of 'Status.OK'. If not, it resets the recommendations and returns 'Status.NOT_FOUND'.
        """
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()

        if movie:
            if any(recommendation is None for recommendation in [movie.recomend1, movie.recomend2, movie.recomend3]):
                self._update_recommendations(movie, gpt_recomendation)
                session.commit()
                session.flush()

            imdb_ids = [movie.recomend1, movie.recomend2, movie.recomend3]
            statuses = self._get_movie_statuses(imdb_ids)

            if all(status == Status.OK for status in statuses):
                movies_query = session.query(Movie).filter(Movie.imdbID.in_(imdb_ids)).limit(3)
                rec_movies_data = movies_query.all()
                return rec_movies_data
            else:
                movie.recomend1 = None
                movie.recomend2 = None
                movie.recomend3 = None
                session.commit()
                return Status.NOT_FOUND
        else:
            return Status.NOT_FOUND

    def recommend_new_movies(self, movie_id):
        """
            Get NEW recommended movies based on a selected movie (.
            Returns a list of dictionaries representing newly recommended movies.

            This method retrieves newly recommended movies for a given movie by RESETTING the existing recommendations
            ('recomend1', 'recomend2', 'recomend3') to None and then updating them using the 'gpt_recomendation_new' function.
            gpt_recommendation_new uses a different request from gpt_recommendation

            It checks the status of recommended movies in the database using '_get_movie_statuses' and returns the data for the recommended
            movies if all have a status of 'Status.OK'. If not, it resets the recommendations and returns 'Status.NOT_FOUND'.
            """
        session = self.Session()
        movie = session.query(Movie).filter_by(id=movie_id).first()

        if movie:
            # Reset recommendations to None (or NULL)
            movie.recomend1 = None
            movie.recomend2 = None
            movie.recomend3 = None
            session.commit()

            self._update_recommendations(movie, gpt_recomendation_new)
            session.commit()
            session.flush()

            imdb_ids = [movie.recomend1, movie.recomend2, movie.recomend3]
            statuses = self._get_movie_statuses(imdb_ids)

            if all(status == Status.OK for status in statuses):
                movies_query = session.query(Movie).filter(Movie.imdbID.in_(imdb_ids)).limit(3)
                rec_movies_data = movies_query.all()

                return rec_movies_data
            else:
                return Status.NOT_FOUND
        else:
            return Status.NOT_FOUND
