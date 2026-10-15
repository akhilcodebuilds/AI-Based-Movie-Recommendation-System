import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load movie dataset
movies = pd.read_csv("data/tmdb_5000_movies.csv")

# Extract genres from JSON data
def extract_genres(genre_data):
    try:
        genres = ast.literal_eval(genre_data)
        return " ".join(genre["name"] for genre in genres)
    except (ValueError, TypeError):
        return ""

movies["genres_text"] = movies["genres"].apply(extract_genres)

# Create movie feature vectors
vectorizer = CountVectorizer()
genre_matrix = vectorizer.fit_transform(movies["genres_text"])

# Calculate similarity between movies
similarity = cosine_similarity(genre_matrix)

# Recommend similar movies
def recommend_movies(movie_title):
    matches = movies[
        movies["title"].str.casefold() == movie_title.strip().casefold()
    ]

    if matches.empty:
        print("Movie not found. Please check the movie title.")
        return

    movie_index = matches.index[0]
    scores = list(enumerate(similarity[movie_index]))
    scores = sorted(scores, key=lambda item: item[1], reverse=True)

    print(f"\nMovies similar to {movies.iloc[movie_index]['title']}:\n")

    count = 0
    for index, score in scores:
        if index != movie_index:
            print(movies.iloc[index]["title"])
            count += 1
        if count == 5:
            break

# Get movie name from user
movie_name = input("Enter a movie name: ")
recommend_movies(movie_name)