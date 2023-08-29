from abc import ABC, abstractmethod
from enum import Enum

class Status(Enum):
    OK = 0
    NOT_FOUND = 1
    ALREADY_ADDED = 2

class DataManagerInterface(ABC):
    @abstractmethod
    def get_user_movies(self, user_id: int, sort: int = 0):
        pass

    @abstractmethod
    def add_new_movie(self, user_id: int, new_movie: str):
        pass

    @abstractmethod
    def movie_info(self, user_id: int, movie_id: int):
        pass

    @abstractmethod
    def movie_update(self, user_id: int, movie_id: int, rating_upd: str, notes_upd: str):
        pass

    @abstractmethod
    def delete_movie(self, user_id: int, movie_id: int):
        pass