import openai
from datamanager.gpt_key import gpt_key

openai.api_key = gpt_key

def gpt_recomendation(movie_title: int):
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
    modify_id = lambda imdb_id: imdb_id if imdb_id.startswith("tt") else "tt" + imdb_id

    return tuple(map(modify_id, (rec.strip() for rec in recomended)))

# test = "tt0119396, tt0133093, tt1375666"
# one, two, three = test.
# print(one)
