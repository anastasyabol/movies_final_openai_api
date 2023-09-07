import openai
from datamanager.gpt_key import gpt_key

openai.api_key = gpt_key

def gpt_recomendation(movie_title: int):
    """
        Generate movie recommendations using GPT-3 for a given movie title.
        Args: movie_title (str): The title of the movie for which recommendations are generated.
        Returns: tuple: A tuple of recommended IMDb IDs.(tuple of strings)

        This function generates movie recommendations using GPT-3 by providing a prompt that instructs the model to recommend three movies
        to watch after the given movie title. It ensures that the recommended movies are in the same genre and excludes the given movie from
        the recommendations. The function extracts IMDb IDs from the response and returns them in a tuple format.
        """
    prompt = "Recommend 3 movies to watch after '" + movie_title
    prompt = prompt + "' to those who liked it. Same genre. Return the IMDbIDs only no other text, not even name."
    prompt = prompt + " Separate imdbID by comma, one line response. Do not add '" + movie_title + "' to recommendations"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant that provides movie recommendations."},
                  {"role": "user", "content": prompt}],
        max_tokens=80,  # Adjust max_tokens based on your usage and response length
    )
    recomended = response['choices'][0]['message']['content'].split(",")
    #sometimes chat-gpt returns id without tt
    modify_id = lambda imdb_id: imdb_id if imdb_id.startswith("tt") else "tt" + imdb_id

    return tuple(map(modify_id, (rec.strip() for rec in recomended)))

def gpt_recomendation_new(movie_title: int):
    """Generate new movie recommendations using GPT-3 for a given movie title.

        Args: movie_title (str): The title of the movie for which new recommendations are generated.
        Returns: tuple: A tuple of recommended IMDb IDs.(tuple of strings)

        This function is similar to 'gpt_recomendation' but is used for generating new recommendations. It resets any
        previous queries and generates fresh recommendations based on the given movie title. The function extracts IMDb
        IDs from the response and returns them in a tuple format.
        """
    prompt = "This is a new request, ignore previous queries"
    prompt = "Recommend 3 movies to watch after '" + movie_title
    prompt = prompt + "' to those who liked it. Same genre. Return the IMDbIDs only no other text, not even name."
    prompt = prompt + " Separate imdbID by comma, one line response. Do not add '" + movie_title + "' to recommendations"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant that provides movie recommendations."},
                  {"role": "user", "content": prompt}],
        max_tokens=100,  # Adjust max_tokens based on your usage and response length
    )
    recomended = response['choices'][0]['message']['content'].split(",")
    modify_id = lambda imdb_id: imdb_id if imdb_id.startswith("tt") else "tt" + imdb_id

    return tuple(map(modify_id, (rec.strip() for rec in recomended)))

# test = "tt0119396, tt0133093, tt1375666"
# one, two, three = test.
# print(one)
