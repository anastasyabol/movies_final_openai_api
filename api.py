from flask import Blueprint, jsonify, request
import json
from app import app, data_manager  # Import the Flask app instance
from flask_login import current_user, login_required, login_user, logout_user
from datamanager.SQLite_data_manager import SQLiteDataManager, Status
from datamanager.database import Movie

import jsonpickle
import random

api_bp = Blueprint('api', __name__, url_prefix='/api')  # Create a Blueprint for the API routes


@api_bp.route('/')
def index():
    random_movie = data_manager.get_user_movies(0)
    return random_movie[0].to_dict()


# Define a route to get random movie data as JSON
@api_bp.route('/random_movie', methods=['GET'])
def get_random_movie():
    random_movie = data_manager.get_user_movies(0)
    return random_movie[0].to_dict()


# Define a route to get user's movies data as JSON
@api_bp.route('/user/<int:id>', methods=['GET', 'POST'])
def user_movies(id: int, sort: int = 0):
    if request.method == 'POST':
        new_movie = request.get_json()
        print(new_movie['title'])
        status = data_manager.add_new_movie(id, new_movie['title'])
        if status == Status.ALREADY_ADDED:
            return jsonify({'Status': 'Error. Already in the library'})
        elif status == Status.NOT_FOUND:
            return jsonify({'Status': 'Error. Not found'})
        elif status == Status.OK:
            return jsonify({'Status': 'OK'})
    else:
        user_movies = data_manager.get_user_movies(id, sort)[::-1] if sort == 0 else data_manager.get_user_movies(id, sort)
        return json.dumps(user_movies, default=lambda x: x.to_dict())


@api_bp.route('/user/<int:id>/update/<int:movie_id>', methods=['POST'])
def update_movies(id: int, movie_id: int):
    update_movie = request.get_json()
    movie_data = data_manager.movie_info(id, movie_id)
    if movie_data is None:
        return jsonify({'Status': 'Error. Not found'})
    rating_upd = update_movie['rating'] if update_movie['rating'] is not None else movie_data.rating
    notes_upd = update_movie['notes'] if update_movie['notes'] is not None else movie_data.notes

    notes = movie_data.get('notes', "")
    print(type(movie_data))
    # Check if the rating might be converted to float
    try:
        float(rating_upd)
    except ValueError:
        return jsonify({'Status': 'Error. Rating must be a number'})
    data_manager.movie_update(id, movie_id, rating_upd, notes_upd)
    return jsonify({'Status': 'OK'})

@api_bp.route('/user/<int:id>/delete/<int:movie_id>', methods=['DELETE'])
def delete_movies(id: int, movie_id: int):
    if not data_manager.delete_movie(id, movie_id):
        return jsonify({'Status': 'Error. Not found'})
    else:
        return jsonify({'Status': 'OK'})


@api_bp.route('/delete/<int:movie_id>', methods=['DELETE'])
def delete_movies_from_db(movie_id: int):
    if not data_manager.delete_from_db(movie_id):
        return jsonify({'Status': 'Error. Not found'})
    else:
        return jsonify({'Status': 'OK'})


# Register the Blueprint with the Flask app
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

