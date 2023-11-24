# Movie Library Web Application

## Overview

This is a Flask-based web application designed for managing a personal movie library. Users can register, log in, and interact with their movie collection. The application integrates with an SQLite database to store user information, movie details, and reviews. Additionally, an API blueprint is included to enable programmatic access to certain functionalities.

**Note: The application uses the OpenAI API to provide movie recommendations based on user preferences.**

## Technologies Used

- **Flask**: A lightweight web framework for Python.
- **Flask-Login**: Manages user sessions and authentication.
- **Flask-SQLAlchemy**: A Flask extension for integrating SQLAlchemy, an SQL toolkit, into the application.
- **SQLite**: A self-contained, serverless, and zero-configuration database engine.
- **OpenAI API**: Utilized for movie recommendations.

## Project Structure

The project contains the following files:

1. **app.py**: Contains the core Flask application, including routes for user authentication, movie management, and the main application logic.

2. **api.py**: Defines an API blueprint extending the application's functionality. It provides endpoints for programmatically interacting with user movies, updates, and deletions.

3. **database.py**: Contains the SQLAlchemy models for movies, user movies, users, and reviews.

4. **data_manager.py**: Implements a data manager interface with methods for interacting with the database, including user movies, reviews, and movie recommendations.

5. **gpt.py**: Integrates functions for generating movie recommendations using the OpenAI GPT-3.5 Turbo model.

6. **gpt_key.py**: Stores the API key for accessing the OpenAI GPT-3.5 Turbo model.

7. **omdb_url.py**: Defines the base URL for making requests to the Open Movie Database (OMDb) API.

8. **requirements.txt**: Lists the project dependencies.


### Prerequisites

- Python installed on your machine.
- Required dependencies installed via `pip install -r requirements.txt`.
- OpenAI API key stored in `gpt_key.py`.

### Usage

### User Interface
Index Page: http://localhost:5002/ - Displays a random movie recommendation.
Registration: http://localhost:5002/register - Create a new user account.
Login: http://localhost:5002/login - Log in with your credentials.
User Library: http://localhost:5002/user/{user_id} - View and manage your movie library.
Movie Recommendations: http://localhost:5002/user/{user_id}/recommend/{movie_id} - Explore movie recommendations.
### API Endpoints
API Index: http://localhost:5002/api/ - Returns a JSON representation of a random movie.
User Movies API: http://localhost:5002/api/user/{user_id} - Get user movies or add a new movie using POST.
Update Movie API: http://localhost:5002/api/user/{user_id}/update/{movie_id} - Update movie details using POST.
Delete Movie API: http://localhost:5002/api/user/{user_id}/delete/{movie_id} - Delete a movie from the user's library.
API Authentication
The API requires authentication using a user's credentials. Ensure that you include the user's ID in the URL when making API requests.

### Important Notes
The project uses an SQLite database located at the specified path. Confirm the database path is correct and accessible.
Ensure the OpenAI API key is set up in gpt_key.py for movie recommendations.
This README assumes the default Flask development server for testing. In a production environment, use a production-ready server.

### Dependencies
Flask
Flask-Login
Flask-SQLAlchemy
OpenAI API (Ensure API credentials are set up for movie recommendations.)
