import os
import re
import pandas as pd

dataset_path = "data/all_movies_clean.csv"
imdb_path = "data/title.basics.tsv.gz"
poster_folder = "static/images/four_genre_posters"

print("Loading movie dataset...")
movies = pd.read_csv(dataset_path).fillna("")

if "poster_url" not in movies.columns:
    movies["poster_url"] = ""

print("Loading poster filenames...")
poster_ids = {}

for root, _, files in os.walk(poster_folder):
    for filename in files:
        match = re.fullmatch(r"(tt\d+)\.jpg", filename, re.IGNORECASE)
        if match:
            imdb_id = match.group(1).lower()
            poster_ids[imdb_id] = (
                "/" + os.path.relpath(
                    os.path.join(root, filename), "."
                ).replace("\\", "/")
            )

print("Available posters:", len(poster_ids))
print("Reading IMDb dataset...")

# Read only IMDb IDs and movie titles
imdb = pd.read_csv(
    imdb_path,
    sep="\t",
    compression="gzip",
    usecols=["tconst", "primaryTitle", "originalTitle"],
    dtype=str,
    na_values="\\N",
    low_memory=False
)

print("Filtering IMDb records for available posters...")

# Keep only records whose IMDb ID has a local poster
imdb = imdb[imdb["tconst"].str.lower().isin(poster_ids)].copy()

def normalize_title(title):
    return re.sub(r"[^a-z0-9]", "", str(title).lower())

# Create title-to-poster mapping
title_to_poster = {}

for row in imdb.itertuples(index=False):
    imdb_id = row.tconst.lower()
    poster = poster_ids[imdb_id]

    for title in (row.primaryTitle, row.originalTitle):
        key = normalize_title(title)
        if key:
            title_to_poster.setdefault(key, poster)

print("Matching movie titles...")

# Vectorized matching instead of iterrows()
movies["title_key"] = movies["title"].map(normalize_title)
matched_posters = movies["title_key"].map(title_to_poster)

movies["poster_url"] = matched_posters.fillna(
    movies["poster_url"]
)

matched = int(matched_posters.notna().sum())

movies.drop(columns=["title_key"], inplace=True)
movies.to_csv(dataset_path, index=False)

print("\nPoster matching completed!")
print("Total movies:", len(movies))
print("Movies matched with posters:", matched)
print("Updated dataset:", dataset_path)