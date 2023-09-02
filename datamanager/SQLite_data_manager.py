from sqlalchemy import create_engine, update, func
from sqlalchemy.orm import sessionmaker
from datamanager.data_manager_interface import DataManagerInterface, Status
from datamanager.database import *
from datamanager.omdb_url import omdb_url
import requests
from datamanager.gpt import gpt_recomendation


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, file_path):
        self.engine = create_engine(file_path)
        self.Session = sessionmaker(bind=self.engine)

    def get_user_movies(self, user_id: int, sort: int = 0):
        """Get the movies for a specific user, sorted based on the given sort parameter. Returns list of dictionaries"""
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
                movie_data = vars(movie)
                print(movie_data['notes'])
                if user_rating is not None:
                    movie_data['rating'] = user_rating
                if user_notes is not None:
                    movie_data['notes'] = user_notes
                result.append(movie_data)
            session.close()
        return result

    def add_new_movie(self, user_id: int, new_movie: str):
        """ """
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

    def add_new_movie_to_db(self, new_movie_title, user_id=0, imdbID=None):
        session = self.Session()
        url = omdb_url + "t="
        request = requests.post(url + new_movie_title + "&plot=full")
        if imdbID is not None:
            url = omdb_url + "i="
            request = requests.post(url + imdbID + "&plot=full")
        api_data = request.json()
        if "Error" in api_data:
            return Status.NOT_FOUND
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
        if new_movie.img == "N/A":
            new_movie.img = 'https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg'
        session.add(new_movie)
        session.flush()
        if user_id != 0:
            user_movie = UserMovie(user_id=user_id, movie_id=new_movie.id)
            session.add(user_movie)
        session.commit()
        session.close()
        return Status.OK

    def movie_info(self, user_id: int, movie_id: int):
        """Get the information of a specific movie for a user."""
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
            return movie_info
        else:
            return None

    def movie_info_by_id(self, movie_id: int):
        """Get the information of a specific movie for a user."""
        session = self.Session()
        query = session.query(Movie).filter(Movie.id == movie_id).first()

        if query:
            movie_info = vars(query)
            session.close()
            return movie_info
        else:
            return None


    def movie_update(self, user_id: int, movie_id: int, rating_upd: str, notes_upd: str):
        session = self.Session()
        update_query = update(UserMovie).where(
            (UserMovie.movie_id == movie_id) & (UserMovie.user_id == user_id)
        ).values(user_rating=rating_upd, user_notes=notes_upd)
        session.execute(update_query)
        session.commit()

        session.close()

    def delete_movie(self, user_id: int, movie_id: int):
        """Delete a movie for a user."""
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
        print(reviews_by_movie)
        return reviews_by_movie

    def add_review(self, new_review_dict):
        session = self.Session()
        new_review = Review(**new_review_dict)
        session.add(new_review)
        session.commit()

    def movie_by_imdbID(self, imdbID):
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

    def recommended_movies(self, movie_id):
        session = self.Session()
        movie_query = session.query(Movie).filter_by(id=movie_id)
        movie = movie_query.first()
        print("********")
        print(movie)

        if movie:
            if movie.recomend1 is None or movie.recomend2 is None or movie.recomend3 is None:
                rec1, rec2, rec3 = gpt_recomendation(movie.title)
                if movie.recomend1 is None:
                    movie.recomend1 = rec1
                if movie.recomend2 is None:
                    movie.recomend2 = rec2
                if movie.recomend3 is None:
                    movie.recomend3 = rec3
                session.commit()
                session.flush()

            imdb_ids = [movie.recomend1, movie.recomend2, movie.recomend3]
            statuses = []

            for imdb_id in imdb_ids:
                status = self.movie_by_imdbID(imdb_id)
                statuses.append(status)

            if all(status == Status.OK for status in statuses):
                # All requests were successful, proceed with querying the database
                movies_query = session.query(Movie).filter(Movie.imdbID.in_(imdb_ids)).limit(3)
                rec_movies_data = movies_query.all()

                for movie in rec_movies_data:
                    print(movie.imdbID, movie.id, movie.title)
                return rec_movies_data
            else:
                return Status.NOT_FOUND

        else:
            return Status.NOT_FOUND

db_uri = "sqlite:////Users/anastasyabolshem/PycharmProjects/masterschool/movies_107.3/datamanager/movies.sqlite"
data_manager = SQLiteDataManager(db_uri)
print(data_manager.recommended_movies(86))