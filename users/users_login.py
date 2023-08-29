from json import load, JSONEncoder
from flask_login import UserMixin
import json

users = {}

class User(UserMixin):
    """User object based on UserMixin - object of Flask-login"""
    max_id = 0
    filename = ""
    def __init__(self, id: str, username: str, email: str, password: str):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self) -> str:
        """Self representation for print of the object"""
        return f"<Id: {self.id}, Username: {self.username}, Email: {self.email}>"

    @staticmethod
    def get(user_id: str):
        """Static method to get a user by user_id"""
        return users.get(user_id)

    @staticmethod
    def get_email(email: str):
        """Static method to get a user by email / to check if email exists to create new_user"""
        match_list = list(filter(lambda x: x.email == email, users.values()))
        print(match_list)
        return match_list[0] if len(match_list) > 0 else None

    @staticmethod
    def load_users(filename):
        """Static method to load users from a JSON file"""
        User.max_id = 0
        User.filename = filename
        with open(filename) as file:
            data = load(file)
            for key in data:
                User.max_id = int(key) if int(key) > User.max_id else User.max_id
                users[key] = User(
                    id=key,
                    username=data[key]["username"],
                    email=data[key]["email"],
                    password=data[key]["password"],
                )

    @staticmethod
    def add_user(name, email, password):
        """Static method to add a new user"""
        User.new_id = User.max_id + 1
        users[str(User.new_id)] = User(str(User.new_id), name, email, password)
        User.dump()
        return User.new_id


    @staticmethod
    def dump():
        """Static method to save the users to a JSON file"""
        with open(User.filename, "w") as handle:
            json.dump(users, handle, cls=UserEncoder)


class UserEncoder(JSONEncoder):
    """JSON encoder for the User class"""
    def default(self, o):
        return o.__dict__


User.load_users('users.json')
User.get_email('lena@lena.ru')