import json
from .data_manager_interface import DataManagerInterface, Status
from .  omdb_url import omdb_url
import requests





class JSONDataManager(DataManagerInterface):
    """Class for managing movie data stored in a JSON file."""

    def __init__(self, file_path: str):
        """Initialize the JSONDataManager with the file path."""
        self._active_user_movies = None
        self.path = file_path
        with open(self.path, "r") as handle:
            self._movies_all_users = json.load(handle)

    def update_file(self):
        """Update the JSON file with the current movie data."""
        with open(self.path, "w") as handle:
            json.dump(self._movies_all_users, handle)


    def get_user_movies(self, user_id: int, sort: int = 0):
        """Get the movies for a specific user, sorted based on the given sort parameter. p = parametr"""
        p = {}
        p[1] = lambda x: int(str(x['year'])[:4])
        p[2] = lambda x: float(x['rating'])
        p[3] = lambda x: -float(x['rating'])
        p[4] = lambda x: x['name']

        self._active_user_movies = list(filter(lambda x: x['id'] == user_id, self._movies_all_users))
        print(self._active_user_movies[0]['movies'])
        if sort == 0:
            return self._active_user_movies[0]['movies']
        elif sort >= 1 and sort <= 4:
            return sorted(self._active_user_movies[0]['movies'], key=p[sort])

    def add_new_user(self, user_id: int, username: str):
        """Add a new user to the data manager."""
        new_data_user = {'id': user_id, 'name': username, 'movies': []}
        self._movies_all_users.append(new_data_user)
        self.update_file()

    def new_movie_is_exist(self, user_id: int, new_movie: str):
        """Check if a new movie already exists for a user."""
        check_new_movie = [x for x in self.get_user_movies(user_id) if x['name'] == new_movie]
        if len(check_new_movie) != 0:
            return True
        else:
            return False

    def movie_is_exist(self, user_id: int, movie_id: int):
        """Check if a movie exists for a user."""
        check_movie = [x for x in self.get_user_movies(user_id) if x['id'] == movie_id]
        if len(check_movie) != 0:
            return True
        else:
            return False

    def new_movie_id(self, user_id: int):
        """Get a new movie ID for a user."""
        try:
            new_movie_id = self.get_user_movies(user_id)[-1]['id'] + 1
        except IndexError:
            new_movie_id = 1
        return new_movie_id

    def add_new_movie(self, user_id: int, new_movie: str):
        """Add a new movie for a user.
        Uses Status object (enum) for statuses of adding. Uses OMDB API to get data"""
        if self.new_movie_is_exist(user_id, new_movie):
            return Status.ALREADY_ADDED
        url = omdb_url
        request = requests.post(url + new_movie + "&plot=full")
        api_data = request.json()
        if "Error" in api_data:
            return Status.NOT_FOUND
        new_movie = {}
        new_movie['id'] = self.new_movie_id(user_id)
        new_movie['title'] = api_data['Title']
        if self.new_movie_is_exist(user_id, api_data['Title']):
            return Status.ALREADY_ADDED
        new_movie['director'] = api_data['Director']
        new_movie['year'] = api_data['Year']
        try:
            new_movie['rating'] = float(api_data['imdbRating'])
        except:
            new_movie['rating'] = 7.77
            new_movie['notes'] = ["Please note: raiting wasn't availible, 7.77 added authomatically"]
        new_movie['img'] = api_data['Poster']
        new_movie['imdbID'] = api_data['imdbID']
        new_movie['plot'] = api_data['Plot']
        self.get_user_movies(user_id).append(new_movie)
        self.update_file()
        return Status.OK

    def movie_info(self, user_id: int, movie_id: int):
        """Get the information of a specific movie for a user."""
        try:
            movie_data = [x for x in self.get_user_movies(user_id) if x['id'] == movie_id][0]
        except IndexError:
            return None
        return movie_data

    def movie_update(self, user_id: int, movie_id: int, rating_upd: str, notes_upd: str):
        """Update the information of a specific movie for a user."""
        movie_to_upd = [movie for item in self._movies_all_users if item['id'] == user_id for movie in item['movies'] if
                        movie['id'] == movie_id][0]
        movie_to_upd.update({
            'rating': rating_upd,
            'notes': notes_upd
        })
        self.update_file()

    def delete_movie(self, user_id: int, movie_id: int):
        """Delete a movie for a user."""
        if not self.movie_is_exist(user_id, movie_id):
            return False
        user_data = list(filter(lambda x: x['id'] == user_id, self._movies_all_users))[0]
        self._movies_all_users = list(filter(lambda x: x['id'] != user_id, self._movies_all_users))
        user_data['movies'] = list(filter(lambda x: x['id'] != movie_id, user_data['movies']))
        self._movies_all_users.append(user_data)
        self.update_file()
        return True


# data_manager = JSONDataManager('movies_data.json')
# data_manager.get_user_movies(1)
