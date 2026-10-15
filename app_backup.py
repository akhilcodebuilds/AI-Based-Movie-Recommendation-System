from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

DATA_FILE = "data/all_movies_clean.csv"


# Load movie dataset
def load_movies():
    movies = pd.read_csv(DATA_FILE).fillna("")

    required_columns = [
        "title",
        "language",
        "genre",
        "overview",
        "year",
        "rating",
        "poster_url"
    ]

    for column in required_columns:
        if column not in movies.columns:
            movies[column] = ""

    for column in required_columns:
        movies[column] = movies[column].astype(str).str.strip()

    movies = movies[movies["title"] != ""].reset_index(drop=True)

    movies["language"] = movies["language"].str.lower()
    movies["features"] = (
        movies["genre"] + " " + movies["overview"]
    ).str.lower()

    return movies


movies = load_movies()

vectorizer = CountVectorizer(stop_words="english")
feature_matrix = vectorizer.fit_transform(movies["features"])


# Home page
@app.route("/")
def home():
    languages = sorted(
        language
        for language in movies["language"].unique()
        if language
    )

    return render_template(
        "index.html",
        languages=languages
    )


# Main movie list
@app.route("/api/movies")
def get_movies():
    language = request.args.get("language", "all").strip().lower()
    search = request.args.get("search", "").strip().lower()
    genre = request.args.get("genre", "").strip().lower()

    filtered = movies.copy()

    # Language filter
    if language and language != "all":
        filtered = filtered[filtered["language"] == language]

    # Movie title search
    if search:
        filtered = filtered[
            filtered["title"].str.lower().str.contains(
                search, regex=False, na=False
            )
        ]

    # Genre filter
    if genre and genre != "all":
        filtered = filtered[
            filtered["genre"].str.lower().str.contains(
                genre, regex=False, na=False
            )
        ]

    # IMPORTANT:
    # Do not remove movies without posters.
    # Keep both types in the same result list.
    results = filtered.head(100)

    response = []

    for _, row in results.iterrows():
        response.append({
            "title": row["title"],
            "year": row["year"],
            "language": row["language"],
            "genre": row["genre"],
            "rating": row["rating"],
            "overview": row["overview"],
            "poster_url": row["poster_url"]
        })

    return jsonify(response)


# Recommend similar movies
@app.route("/api/recommend")
def recommend():
    title = request.args.get("title", "").strip()
    language = request.args.get("language", "all").strip().lower()

    matches = movies[
        movies["title"].str.lower() == title.lower()
    ]

    if language and language != "all":
        matches = matches[matches["language"] == language]

    if matches.empty:
        return jsonify({
            "error": "Movie not found for the selected language."
        }), 404

    movie_index = matches.index[0]
    movie_language = movies.iloc[movie_index]["language"]

    scores = cosine_similarity(
        feature_matrix[movie_index],
        feature_matrix
    ).flatten()

    ranked_indices = sorted(
        enumerate(scores),
        key=lambda item: item[1],
        reverse=True
    )

    recommendations = []

    for index, score in ranked_indices:
        if index == movie_index:
            continue

        if movies.iloc[index]["language"] != movie_language:
            continue

        row = movies.iloc[index]

        recommendations.append({
            "title": row["title"],
            "year": row["year"],
            "language": row["language"],
            "genre": row["genre"],
            "rating": row["rating"],
            "overview": row["overview"],
            "poster_url": row["poster_url"],
            "similarity": round(float(score), 3)
        })

        if len(recommendations) == 10:
            break

    return jsonify(recommendations)


if __name__ == "__main__":
    app.run(debug=True)