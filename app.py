from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack

app = Flask(__name__)

DATA_FILE = "data/all_movies_clean.csv"


# Load and clean movie dataset
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

        movies[column] = movies[column].astype(str).str.strip()

    movies = movies[movies["title"] != ""].reset_index(drop=True)

    movies["language"] = movies["language"].str.lower()
    movies["genre"] = movies["genre"].str.lower()
    movies["overview"] = movies["overview"].str.lower()

    # Give genre more importance than overview
    movies["genre_features"] = movies["genre"].apply(
        lambda value: (value + " ") * 3
    )

    return movies


movies = load_movies()

# Convert genre and overview into TF-IDF features
genre_vectorizer = TfidfVectorizer(stop_words="english")
overview_vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=20000
)

genre_matrix = genre_vectorizer.fit_transform(
    movies["genre_features"]
)

overview_matrix = overview_vectorizer.fit_transform(
    movies["overview"]
)

# Combine both feature matrices
feature_matrix = hstack([
    genre_matrix,
    overview_matrix
]).tocsr()


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

    filtered = movies

    if language and language != "all":
        filtered = filtered[filtered["language"] == language]

    if search:
        filtered = filtered[
            filtered["title"].str.lower().str.contains(
                search,
                regex=False,
                na=False
            )
        ]

    if genre and genre != "all":
        filtered = filtered[
            filtered["genre"].str.contains(
                genre,
                regex=False,
                na=False
            )
        ]

    results = filtered.head(100)

    return jsonify([
        {
            "title": row["title"],
            "year": row["year"],
            "language": row["language"],
            "genre": row["genre"],
            "rating": row["rating"],
            "overview": row["overview"],
            "poster_url": row["poster_url"]
        }
        for _, row in results.iterrows()
    ])


# Recommend similar movies
@app.route("/api/recommend")
def recommend():
    title = request.args.get("title", "").strip()
    language = request.args.get("language", "all").strip().lower()

    if not title:
        return jsonify({"error": "Please provide a movie title."}), 400

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
    seen_titles = {title.lower()}

    for index, score in ranked_indices:
        if index == movie_index:
            continue

        row = movies.iloc[index]

        if row["language"] != movie_language:
            continue

        candidate_title = row["title"].lower()

        if candidate_title in seen_titles:
            continue

        # Ignore movies with no meaningful similarity
        if score <= 0:
            continue

        seen_titles.add(candidate_title)

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

        if len(recommendations) >= 10:
            break

    return jsonify(recommendations)


if __name__ == "__main__":
    app.run(debug=True)