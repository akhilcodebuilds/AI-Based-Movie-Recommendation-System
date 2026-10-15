import pandas as pd
import os

DATA_FILE = "data/all_movies_clean.csv"

print("=" * 45)
print("MOVIE RECOMMENDATION SYSTEM")
print("DATASET VERIFICATION")
print("=" * 45)

if not os.path.exists(DATA_FILE):
    print("ERROR: Dataset file not found!")
    raise SystemExit(1)

movies = pd.read_csv(DATA_FILE).fillna("")

print("Total Movies:", len(movies))

required_columns = [
    "title",
    "year",
    "language",
    "genre",
    "rating",
    "overview",
    "poster_url"
]

print("\nColumn Verification:")

for column in required_columns:
    if column in movies.columns:
        print(f"{column}: Available")
    else:
        print(f"{column}: Missing")

if "title" in movies.columns:
    print("\nMovies with titles:", (movies["title"].astype(str).str.strip() != "").sum())

if "poster_url" in movies.columns:
    has_poster = movies["poster_url"].astype(str).str.strip() != ""
    print("Movies with poster paths:", has_poster.sum())
    print("Movies without poster paths:", (~has_poster).sum())

print("\nDataset verification completed.")
print("\nChecking actual poster files...")

if "poster_url" in movies.columns:
    poster_paths = movies["poster_url"].astype(str).str.strip()
    poster_paths = poster_paths[poster_paths != ""]

    existing = 0
    missing = 0

    for path in poster_paths:
        relative_path = path.lstrip("/").replace("/", os.sep)

        if os.path.isfile(relative_path):
            existing += 1
        else:
            missing += 1

    print("Existing poster files:", existing)
    print("Missing poster files:", missing)