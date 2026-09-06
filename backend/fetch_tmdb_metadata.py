import os
import re
import time
import requests

from dotenv import load_dotenv
from sqlalchemy import text
from database import engine


# ============================================================
# 1. LOAD .ENV
# ============================================================

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError(
        "TMDB_API_KEY not found. Check your backend/.env file."
    )


# ============================================================
# 2. CONFIGURATION
# ============================================================

TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.tmdb.org/3")

# Small delay to avoid hammering TMDB
REQUEST_DELAY = 0.25

# Maximum time a single request can wait
REQUEST_TIMEOUT = (5, 15)


# ============================================================
# 3. HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "Accept": "application/json",
    "User-Agent": "CineMatch-AI/1.0"
})


# ============================================================
# 4. PARSE MOVIELENS TITLE
# ============================================================

def parse_movielens_title(title):

    match = re.search(
        r"\s*\((\d{4})\)\s*$",
        title
    )

    if match:

        year = int(match.group(1))

        clean_title = re.sub(
            r"\s*\(\d{4}\)\s*$",
            "",
            title
        ).strip()

        return clean_title, year

    return title.strip(), None


# ============================================================
# 5. BUILD POSSIBLE SEARCH TITLES
# ============================================================

def build_search_titles(title):

    clean_title, year = parse_movielens_title(title)

    candidates = []

    def add_candidate(value):

        value = value.strip()

        if value and value not in candidates:
            candidates.append(value)

    # Original cleaned title
    add_candidate(clean_title)

    # Remove "(a.k.a. ...)"
    without_aka = re.sub(
        r"\s*\(a\.k\.a\.[^)]*\)",
        "",
        clean_title,
        flags=re.IGNORECASE
    ).strip()

    add_candidate(without_aka)

    # Remove alternate title in parentheses
    primary_title = re.split(
        r"\s*\(",
        without_aka,
        maxsplit=1
    )[0].strip()

    add_candidate(primary_title)

    return candidates, year


# ============================================================
# 6. NORMALIZE TITLE
# ============================================================

def normalize_title(title):

    title = title.lower().strip()

    # MovieLens sometimes stores:
    # American President, The
    #
    # Convert to:
    # The American President

    if title.endswith(", the"):
        title = "the " + title[:-5]

    elif title.endswith(", a"):
        title = "a " + title[:-3]

    elif title.endswith(", an"):
        title = "an " + title[:-4]

    # Remove punctuation
    title = re.sub(
        r"[^a-z0-9\s]",
        "",
        title
    )

    # Remove extra spaces
    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title


# ============================================================
# 7. SEARCH TMDB
# ============================================================

def search_tmdb(title, year=None):

    url = f"{TMDB_BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "include_adult": "false",
        "language": "en-US",
        "page": 1
    }

    if year:
        params["year"] = year

    try:

        response = session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])

    except requests.exceptions.Timeout:

        print("      ⏱ TMDB request timed out.")
        return []

    except requests.exceptions.RequestException as e:

        print(f"      ❌ TMDB request error: {e}")
        return []

    except ValueError:

        print("      ❌ Invalid TMDB JSON response.")
        return []


# ============================================================
# 8. FIND BEST MATCH
# ============================================================

def find_best_match(
    movielens_title,
    movielens_year,
    results
):

    if not results:
        return None

    normalized_ml_title = normalize_title(
        movielens_title
    )

    candidates = []

    for movie in results:

        tmdb_title = movie.get(
            "title",
            ""
        )

        original_title = movie.get(
            "original_title",
            ""
        )

        release_date = movie.get(
            "release_date",
            ""
        )

        tmdb_year = None

        if release_date:

            try:
                tmdb_year = int(
                    release_date[:4]
                )
            except ValueError:
                tmdb_year = None

        normalized_tmdb_title = normalize_title(
            tmdb_title
        )

        normalized_original_title = normalize_title(
            original_title
        )

        # ----------------------------------------------------
        # TITLE MATCH
        # ----------------------------------------------------

        title_match = (
            normalized_ml_title == normalized_tmdb_title
            or
            normalized_ml_title == normalized_original_title
        )

        # ----------------------------------------------------
        # YEAR MATCH
        # ----------------------------------------------------

        year_match = False

        if movielens_year and tmdb_year:

            year_match = (
                movielens_year == tmdb_year
            )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score = 0

        if title_match:
            score += 100

        if year_match:
            score += 100

        # Allow one-year difference
        if (
            movielens_year
            and tmdb_year
            and abs(movielens_year - tmdb_year) <= 1
        ):
            score += 20

        popularity = movie.get(
            "popularity",
            0
        )

        try:
            score += min(
                float(popularity),
                20
            )
        except (ValueError, TypeError):
            pass

        candidates.append(
            (
                score,
                movie,
                title_match,
                year_match
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    best = candidates[0]

    movie = best[1]
    title_match = best[2]
    year_match = best[3]

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if movielens_year:

        if not title_match or not year_match:
            return None

    else:

        if not title_match:
            return None

    return movie


# ============================================================
# 9. FIND TMDB MATCH
# ============================================================

def find_tmdb_match(title):

    candidates, year = build_search_titles(title)

    for candidate in candidates:

        print(
            f"      🔎 Searching: {candidate}"
        )

        results = search_tmdb(
            candidate,
            year
        )

        match = find_best_match(
            candidate,
            year,
            results
        )

        if match:
            return match

        # Very small delay between alternate searches
        time.sleep(0.1)

    return None


# ============================================================
# 10. GET FULL TMDB DETAILS
# ============================================================

def get_movie_details(tmdb_id):

    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    try:

        response = session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:

        print(
            "      ⏱ Details request timed out."
        )

        return None

    except requests.exceptions.RequestException as e:

        print(
            f"      ❌ Details request error: {e}"
        )

        return None

    except ValueError:

        print(
            "      ❌ Invalid TMDB details response."
        )

        return None


# ============================================================
# 11. UPDATE MYSQL
# ============================================================

def update_movie(movie_id, tmdb_data):

    release_date = tmdb_data.get(
        "release_date"
    )

    release_year = None

    if release_date:

        try:
            release_year = int(
                release_date[:4]
            )
        except ValueError:
            release_year = None

    # Poster
    poster_path = tmdb_data.get(
        "poster_path"
    )

    poster_url = None

    if poster_path:

        poster_url = (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    # Backdrop
    backdrop_path = tmdb_data.get(
        "backdrop_path"
    )

    backdrop_url = None

    if backdrop_path:

        backdrop_url = (
            "https://image.tmdb.org/t/p/w1280"
            + backdrop_path
        )

    tmdb_id = tmdb_data.get(
        "id"
    )

    overview = tmdb_data.get(
        "overview"
    )

    runtime = tmdb_data.get(
        "runtime"
    )

    # --------------------------------------------------------
    # SAVE TO MYSQL
    # --------------------------------------------------------

    with engine.begin() as connection:

        connection.execute(

            text("""
                UPDATE movies

                SET
                    release_year = :release_year,
                    tmdb_id = :tmdb_id,
                    poster_url = :poster_url,
                    backdrop_url = :backdrop_url,
                    overview = :overview,
                    runtime = :runtime

                WHERE movie_id = :movie_id
            """),

            {
                "release_year": release_year,
                "tmdb_id": tmdb_id,
                "poster_url": poster_url,
                "backdrop_url": backdrop_url,
                "overview": overview,
                "runtime": runtime,
                "movie_id": movie_id
            }
        )


# ============================================================
# 12. MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("       CINEMATCH-AI MOVIELENS → TMDB IMPORTER")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # GET ONLY MOVIES THAT DO NOT HAVE TMDB ID
    # --------------------------------------------------------

    with engine.connect() as connection:

        movies = connection.execute(

            text("""
                SELECT
                    movie_id,
                    title

                FROM movies

                WHERE tmdb_id IS NULL

                ORDER BY movie_id
            """)

        ).mappings().all()

    total = len(movies)

    print(
        f"Movies remaining: {total}"
    )

    print()

    if total == 0:

        print(
            "🎉 All movies already have TMDB metadata."
        )

        return

    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    success = 0
    not_found = 0
    failed = 0

    failed_movies = []

    # --------------------------------------------------------
    # PROCESS MOVIES
    # --------------------------------------------------------

    for index, movie in enumerate(
        movies,
        start=1
    ):

        movie_id = movie["movie_id"]
        original_title = movie["title"]

        print()
        print("-" * 70)

        print(
            f"[{index}/{total}] Movie ID: {movie_id}"
        )

        print(
            f"MovieLens: {original_title}"
        )

        try:

            # ------------------------------------------------
            # SEARCH + MATCH
            # ------------------------------------------------

            match = find_tmdb_match(
                original_title
            )

            if not match:

                print(
                    "      ⚠️ No reliable TMDB match"
                )

                not_found += 1

                failed_movies.append({

                    "movie_id": movie_id,

                    "title": original_title,

                    "reason": "No reliable match"

                })

                time.sleep(
                    REQUEST_DELAY
                )

                continue

            # ------------------------------------------------
            # MATCH FOUND
            # ------------------------------------------------

            tmdb_id = match.get(
                "id"
            )

            tmdb_title = match.get(
                "title"
            )

            release_date = match.get(
                "release_date"
            )

            print(
                f"      ✅ Match: {tmdb_title}"
            )

            print(
                f"      🆔 TMDB ID: {tmdb_id}"
            )

            print(
                f"      📅 Release: {release_date}"
            )

            # ------------------------------------------------
            # GET DETAILS
            # ------------------------------------------------

            details = get_movie_details(
                tmdb_id
            )

            if not details:

                print(
                    "      ❌ Could not get full details"
                )

                failed += 1

                failed_movies.append({

                    "movie_id": movie_id,

                    "title": original_title,

                    "reason": "Details request failed"

                })

                time.sleep(
                    REQUEST_DELAY
                )

                continue

            # ------------------------------------------------
            # SAVE TO MYSQL
            # ------------------------------------------------

            update_movie(
                movie_id,
                details
            )

            poster_exists = bool(
                details.get("poster_path")
            )

            backdrop_exists = bool(
                details.get("backdrop_path")
            )

            runtime = details.get(
                "runtime"
            )

            print(
                f"      🖼 Poster: "
                f"{'YES' if poster_exists else 'NO'}"
            )

            print(
                f"      🌄 Backdrop: "
                f"{'YES' if backdrop_exists else 'NO'}"
            )

            print(
                f"      ⏱ Runtime: "
                f"{runtime if runtime else 'N/A'} min"
            )

            print(
                "      💾 Saved to MySQL"
            )

            success += 1

        except KeyboardInterrupt:

            print()
            print()

            print(
                "⚠️ Process stopped by user."
            )

            print(
                "Already saved movies remain in MySQL."
            )

            break

        except Exception as e:

            print(
                f"      ❌ Unexpected error: {e}"
            )

            failed += 1

            failed_movies.append({

                "movie_id": movie_id,

                "title": original_title,

                "reason": str(e)

            })

        # ----------------------------------------------------
        # DELAY
        # ----------------------------------------------------

        time.sleep(
            REQUEST_DELAY
        )

    # ========================================================
    # SAVE FAILED MOVIES
    # ========================================================

    if failed_movies:

        with open(
            "tmdb_failed_movies.txt",
            "w",
            encoding="utf-8"
        ) as file:

            for movie in failed_movies:

                file.write(

                    f"{movie['movie_id']} | "
                    f"{movie['title']} | "
                    f"{movie['reason']}\n"

                )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print()

    print("=" * 70)
    print("                  IMPORT COMPLETE")
    print("=" * 70)

    print(
        f"✅ Successful : {success}"
    )

    print(
        f"⚠️ Not found  : {not_found}"
    )

    print(
        f"❌ Failed     : {failed}"
    )

    print(
        f"📊 Processed  : "
        f"{success + not_found + failed}"
    )

    print("=" * 70)
    print()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()

