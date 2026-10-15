import pandas as pd
import os
import ast
import re

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "all_movies_clean.csv")

movies = []


def clean_text(value):
    """Convert missing values to empty strings and clean whitespace."""
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_language(value):
    """Normalize language names and common combined-language entries."""
    language = clean_text(value).lower()

    if not language or language == "nan":
        return "unknown"

    # Standardize common spelling variations.
    aliases = {
        "oriya": "odia",
        "rajastani": "rajasthani",
    }

    # Separate languages written together using newline or slash.
    language = language.replace("/", ",")
    parts = [part.strip() for part in language.split(",") if part.strip()]

    if len(parts) == 1:
        # Handle values such as "telugu tamil" or "telugu hindi".
        words = parts[0].split()

        if len(words) > 1 and all(
            word in {
                "telugu", "hindi", "tamil", "malayalam", "kannada",
                "bengali", "marathi", "punjabi", "gujarati", "urdu",
                "english", "odia", "assamese", "bhojpuri"
            }
            for word in words
        ):
            return aliases.get(words[0], words[0])

        return aliases.get(parts[0], parts[0])

    # For a movie with multiple languages, use the first listed language.
    return aliases.get(parts[0], parts[0])


def add_movie(title, year, language, genre, rating, overview, source):
    title = clean_text(title)

    if not title:
        return

    movies.append({
        "title": title,
        "year": clean_text(year),
        "language": clean_language(language),
        "genre": clean_text(genre),
        "rating": clean_text(rating),
        "overview": clean_text(overview),
        "source": source
    })


# 1. Indian movies dataset
indian_path = os.path.join(DATA_DIR, "indian movies.csv")

if os.path.exists(indian_path):
    df = pd.read_csv(indian_path, low_memory=False)

    for _, row in df.iterrows():
        add_movie(
            row.get("Movie Name", ""),
            row.get("Year", ""),
            row.get("Language", ""),
            row.get("Genre", ""),
            row.get("Rating(10)", ""),
            "",
            "Indian Movies"
        )


# 2. Highest grossing Indian movies
gross_path = os.path.join(DATA_DIR, "Highest grossing Indian movies.csv")

if os.path.exists(gross_path):
    df = pd.read_csv(gross_path, low_memory=False)

    for _, row in df.iterrows():
        add_movie(
            row.get("Film", ""),
            row.get("Year", ""),
            row.get("Primary Language", ""),
            "",
            "",
            "",
            "Highest Grossing"
        )


# 3. TMDB movies dataset
tmdb_path = os.path.join(DATA_DIR, "tmdb_5000_movies.csv")

if os.path.exists(tmdb_path):
    df = pd.read_csv(tmdb_path, low_memory=False)

    for _, row in df.iterrows():
        try:
            genre_items = ast.literal_eval(str(row.get("genres", "[]")))
            genre = ", ".join(
                item.get("name", "") for item in genre_items
            )
        except (ValueError, SyntaxError, TypeError):
            genre = ""

        add_movie(
            row.get("title", ""),
            str(row.get("release_date", ""))[:4],
            row.get("original_language", ""),
            genre,
            row.get("vote_average", ""),
            row.get("overview", ""),
            "TMDB"
        )


# 4. Combine and clean datasets
result = pd.DataFrame(movies)

result = result.drop_duplicates(
    subset=["title", "language"],
    keep="first"
).reset_index(drop=True)

os.makedirs(DATA_DIR, exist_ok=True)
result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("Dataset preparation completed!")
print("Total movies:", len(result))
print("Languages found:", result["language"].nunique())
print("\nTop 20 languages:")
print(result["language"].value_counts().head(20).to_string())
print("\nSaved to:", OUTPUT_FILE)