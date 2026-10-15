const searchInput = document.getElementById("searchInput");
const languageFilter = document.getElementById("languageFilter");
const genreInput = document.getElementById("genreInput");
const searchButton = document.getElementById("searchButton");
const clearFiltersButton = document.getElementById("clearFiltersButton");
const movieFilterForm = document.getElementById("movieFilterForm");

const moviesGrid = document.getElementById("moviesGrid");
const resultsTitle = document.getElementById("resultsTitle");
const statusMessage = document.getElementById("statusMessage");
const watchlistGrid = document.getElementById("watchlistGrid");

let watchlist = [];

try {
    watchlist = JSON.parse(
        localStorage.getItem("cineverseWatchlist") || "[]"
    );

    if (!Array.isArray(watchlist)) {
        watchlist = [];
    }
} catch (error) {
    watchlist = [];
}

function createElement(tag, className, text = "") {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = text;
    return element;
}

function showMessage(container, message) {
    container.replaceChildren(
        createElement("p", "loading-message", message)
    );
}

function isInWatchlist(movie) {
    return watchlist.some(function (item) {
        return item.title === movie.title &&
            item.language === movie.language;
    });
}

function saveWatchlist() {
    localStorage.setItem(
        "cineverseWatchlist",
        JSON.stringify(watchlist)
    );
}

function createMovieCard(movie, isWatchlist = false) {
    const card = createElement("article", "movie-card");

    const poster = createElement("div", "movie-poster");

    if (movie.poster_url && movie.poster_url.trim() !== "") {
        const image = document.createElement("img");

        image.src = new URL(
            movie.poster_url,
            window.location.origin
        ).href;

        image.alt = (movie.title || "Movie") + " poster";
        image.loading = "lazy";

        image.onerror = function () {
            image.remove();

            if (!poster.querySelector(".poster-title")) {
                poster.appendChild(
                    createElement(
                        "span",
                        "poster-title",
                        movie.title || "Poster unavailable"
                    )
                );
            }
        };

        poster.appendChild(image);
    } else {
        poster.appendChild(
            createElement(
                "span",
                "poster-title",
                movie.title || "Poster unavailable"
            )
        );
    }

    const info = createElement("div", "movie-info");

    info.appendChild(
        createElement(
            "h3",
            "movie-title",
            movie.title || "Unknown Movie"
        )
    );

    const year = movie.year || "Year N/A";

    const language = movie.language
        ? movie.language.charAt(0).toUpperCase() +
          movie.language.slice(1)
        : "Language N/A";

    info.appendChild(
        createElement("p", "movie-meta", year + " • " + language)
    );

    info.appendChild(
        createElement(
            "p",
            "movie-rating",
            "★ " + (movie.rating || "N/A")
        )
    );

    info.appendChild(
        createElement(
            "p",
            "movie-genre",
            movie.genre || "Genre unavailable"
        )
    );

    if (movie.overview) {
        info.appendChild(
            createElement("p", "movie-overview", movie.overview)
        );
    }

    const actions = createElement("div", "card-actions");

    if (isWatchlist) {
        const removeButton = createElement(
            "button",
            "card-button",
            "Remove"
        );

        removeButton.type = "button";

        removeButton.addEventListener("click", function () {
            watchlist = watchlist.filter(function (item) {
                return !(
                    item.title === movie.title &&
                    item.language === movie.language
                );
            });

            saveWatchlist();
            displayWatchlist();
            loadMovies();
        });

        actions.appendChild(removeButton);
    } else {
        const saved = isInWatchlist(movie);

        const watchlistButton = createElement(
            "button",
            "card-button",
            saved ? "Saved ✓" : "+ Watchlist"
        );

        watchlistButton.type = "button";
        watchlistButton.disabled = saved;

        watchlistButton.addEventListener("click", function () {
            if (!isInWatchlist(movie)) {
                watchlist.push(movie);
                saveWatchlist();
                displayWatchlist();

                watchlistButton.textContent = "Saved ✓";
                watchlistButton.disabled = true;
            }
        });

        actions.appendChild(watchlistButton);

        const recommendButton = createElement(
            "button",
            "card-button recommend-button",
            "Similar Movies"
        );

        recommendButton.type = "button";

        recommendButton.addEventListener("click", function () {
            getRecommendations(movie);
        });

        actions.appendChild(recommendButton);
    }

    info.appendChild(actions);
    card.append(poster, info);

    return card;
}

function displayWatchlist() {
    watchlistGrid.replaceChildren();

    if (watchlist.length === 0) {
        showMessage(watchlistGrid, "Your watchlist is empty.");
        return;
    }

    watchlist.forEach(function (movie) {
        watchlistGrid.appendChild(createMovieCard(movie, true));
    });
}

async function loadMovies() {
    showMessage(moviesGrid, "Loading movies...");
    statusMessage.textContent = "";

    const params = new URLSearchParams({
        language: languageFilter.value,
        search: searchInput.value.trim(),
        genre: genreInput.value.trim()
    });

    try {
        const response = await fetch("/api/movies?" + params.toString());

        if (!response.ok) {
            throw new Error("Unable to load movies.");
        }

        const movies = await response.json();

        moviesGrid.replaceChildren();

        if (movies.length === 0) {
            showMessage(
                moviesGrid,
                "No movies found. Try different filters."
            );

            resultsTitle.textContent = "No Results";
            statusMessage.textContent = "Try changing your search or filters.";
            return;
        }

        movies.forEach(function (movie) {
            moviesGrid.appendChild(createMovieCard(movie));
        });

        resultsTitle.textContent = "Movies You May Like";

        statusMessage.textContent =
            "Showing " + movies.length + " movies.";
    } catch (error) {
        showMessage(
            moviesGrid,
            "Could not load movies. Check whether the Flask server is running."
        );

        console.error(error);
    }
}

async function getRecommendations(movie) {
    resultsTitle.textContent = "Movies Similar to " + movie.title;

    showMessage(moviesGrid, "Finding similar movies...");
    statusMessage.textContent = "";

    const params = new URLSearchParams({
        title: movie.title,
        language: movie.language || "all"
    });

    try {
        const response = await fetch(
            "/api/recommend?" + params.toString()
        );

        const data = await response.json();

        moviesGrid.replaceChildren();

        if (!response.ok) {
            showMessage(
                moviesGrid,
                data.error || "Could not find recommendations."
            );
            return;
        }

        if (data.length === 0) {
            showMessage(
                moviesGrid,
                "No similar movies found for this language."
            );
            return;
        }

        data.forEach(function (recommendedMovie) {
            moviesGrid.appendChild(
                createMovieCard(recommendedMovie)
            );
        });

        statusMessage.textContent =
            "Found " + data.length +
            " similar movies in " + movie.language + ".";

    } catch (error) {
        showMessage(
            moviesGrid,
            "Recommendation failed. Please try again."
        );

        console.error(error);
    }
}

// Search form submission
if (movieFilterForm) {
    movieFilterForm.addEventListener("submit", function (event) {
        event.preventDefault();
        loadMovies();
    });
} else {
    searchButton.addEventListener("click", loadMovies);
}

// Enter key support
searchInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !movieFilterForm) {
        loadMovies();
    }
});

genreInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !movieFilterForm) {
        loadMovies();
    }
});

// Language filter
languageFilter.addEventListener("change", loadMovies);

// Clear all filters
if (clearFiltersButton) {
    clearFiltersButton.addEventListener("click", function () {
        searchInput.value = "";
        languageFilter.value = "all";
        genreInput.value = "";

        loadMovies();
    });
}

// Initial page load
displayWatchlist();
loadMovies();