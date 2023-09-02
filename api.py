from flask import Blueprint, jsonify
from app import app, data_manager  # Import the Flask app instance
from datamanager.json_data_manager import *  # Import necessary modules and classes
import random

api_bp = Blueprint('api', __name__, url_prefix='/api')  # Create a Blueprint for the API routes

# Define a route to get random movie data as JSON
@api_bp.route('/random_movie', methods=['GET'])
def get_random_movie():
    random_movie = random.choice(data_manager.get_user_movies(0))
    return jsonify(random_movie)

# Define a route to get user's movies data as JSON
@api_bp.route('/user_movies/<int:id>', methods=['GET'])
def get_user_movies(id):
    user_movies = data_manager.get_user_movies(id)
    return jsonify(user_movies)

# Define other API routes as needed

# ...

# Register the Blueprint with the Flask app
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
