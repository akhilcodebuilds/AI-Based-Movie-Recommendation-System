# AI-Based Movie Recommendation System

An AI-powered movie recommendation web application that helps users discover movies based on their interests. The system uses content-based filtering to recommend movies with similar genres and descriptions.

## About the Project

The AI-Based Movie Recommendation System is developed using Python and Flask. It allows users to search for movies, filter results by language and genre, and receive recommendations based on movie content.

The project uses TF-IDF vectorization and cosine similarity to compare movie features and identify similar movies.

## Features

* Search for movies by title.
* Filter movies by language and genre.
* Get recommendations for similar movies.
* Display movie details, including genre, language, year, and rating.
* View movie posters where available.
* Maintain a watchlist.
* Use a responsive web interface.

## Technologies Used

* **Programming Language:** Python
* **Web Framework:** Flask
* **Data Processing:** Pandas
* **Machine Learning:** Scikit-learn
* **Recommendation Technique:** TF-IDF and Cosine Similarity
* **Frontend:** HTML, CSS, JavaScript
* **Version Control:** Git and GitHub

## Project Structure

```text
AI-Based-Movie-Recommendation-System/
├── app.py
├── recommend.py
├── prepare_data.py
├── check_data.py
├── match_posters.py
├── data/
│   └── all_movies_clean.csv
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── images/
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/akhilcodebuilds/AI-Based-Movie-Recommendation-System.git
```

### 2. Open the Project Folder

```bash
cd AI-Based-Movie-Recommendation-System
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Required Libraries

```bash
pip install flask pandas scikit-learn
```

### 6. Run the Application

```bash
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000/
```

## How It Works

1. The application loads movie information from the dataset.
2. Movie genres and descriptions are converted into numerical text features using TF-IDF.
3. Cosine similarity measures how closely movie features match.
4. The system ranks similar movies and displays recommendations.
5. Users can explore movies using search and filtering options.

## Dataset

The project uses a cleaned movie dataset stored in the `data` folder.

The dataset contains information such as movie titles, languages, genres, release years, ratings, and descriptions.

## Future Improvements

* Add user login and personalized recommendations.
* Improve movie poster coverage.
* Add advanced recommendation algorithms.
* Deploy the application online.
* Expand and update the movie dataset.

## Author

**Akhil Kumar**

GitHub: [akhilcodebuilds](https://github.com/akhilcodebuilds)

## License

This project was developed for educational and portfolio purposes.