import openai
from gpt_key import gpt_key

openai.api_key = gpt_key
movie_title = "'Titanic'"
prompt = "Recommend 3 movies to watch after " + movie_title
prompt = prompt + " to those who liked it. Return the IMDbIDs only no other text, not even name."
prompt = " Separate imdbID by comma, one line response. Do not add " + movie_title + " to recommendations"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "You are a helpful assistant that provides movie recommendations."},
              {"role": "user", "content": prompt}],
    max_tokens=100,  # Adjust max_tokens based on your usage and response length
)

print(response)
print("****")
print(response['choices'][0])
modify_id = lambda imdb_id: imdb_id if imdb_id.startswith("tt") else "tt" + imdb_id
recomended = response['choices'][0]['message']['content'].split(",")
print("****")
print(modify_id(recomended[0].strip()))
print(modify_id(recomended[1].strip()))
print(modify_id(recomended[2].strip()))

# test = "tt0119396, tt0133093, tt1375666"
# one, two, three = test.
# print(one)
