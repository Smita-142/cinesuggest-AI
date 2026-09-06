import os
import requests

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
from models import Movie


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


# ============================================================
# TMDB CONFIGURATION
# ============================================================

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"


tmdb_session = requests.Session()

tmdb_session.headers.update({
    "Accept": "application/json",
    "User-Agent": "CineMatch-AI/1.0"
})


# ============================================================
# GET ALL MOVIES
# ============================================================

@router.get("/")
def get_movies(
    db: Session = Depends(get_db)
):

    movies = (
        db.query(Movie)
        .limit(20)
        .all()
    )

    return movies


# ============================================================
# SEARCH MOVIES
# ============================================================

@router.get("/search")
def search_movies(
    title: str = Query(...),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # FIRST SEARCH MYSQL
    # --------------------------------------------------------

    movies = (
        db.query(Movie)
        .filter(
            Movie.title.ilike(f"%{title}%")
        )
        .limit(20)
        .all()
    )


    if movies:

        return {
            "source": "database",
            "results": movies
        }


    # --------------------------------------------------------
    # IF NOT FOUND -> SEARCH TMDB
    # --------------------------------------------------------

    if not TMDB_API_KEY:

        return {
            "source": "none",
            "results": [],
            "message": "Movie not found."
        }


    try:

        response = tmdb_session.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": title,
                "language": "en-US",
                "include_adult": "false"
            },
            timeout=10
        )


        if not response.ok:

            return {
                "source": "none",
                "results": [],
                "message": "Movie not found."
            }


        data = response.json()


        results = []


        for movie in data.get("results", []):

            poster_url = None

            backdrop_url = None


            if movie.get("poster_path"):

                poster_url = (
                    "https://image.tmdb.org/t/p/w500"
                    + movie["poster_path"]
                )


            if movie.get("backdrop_path"):

                backdrop_url = (
                    "https://image.tmdb.org/t/p/w1280"
                    + movie["backdrop_path"]
                )


            results.append({

                "movie_id": None,

                "tmdb_id": movie.get("id"),

                "title": movie.get("title"),

                "overview": movie.get("overview"),

                "release_date":
                    movie.get("release_date"),

                "release_year":
                    (
                        movie.get("release_date", "")[:4]
                        if movie.get("release_date")
                        else None
                    ),

                "rating":
                    movie.get("vote_average"),

                "vote_count":
                    movie.get("vote_count"),

                "popularity":
                    movie.get("popularity"),

                "poster_url":
                    poster_url,

                "backdrop_url":
                    backdrop_url,

                "source": "tmdb"

            })


        return {
            "source": "tmdb",
            "results": results
        }


    except Exception as error:

        print(
            "TMDB search error:",
            error
        )

        return {
            "source": "none",
            "results": [],
            "message": "Unable to search TMDB."
        }


# ============================================================
# TOP RATED MOVIES
# ============================================================

@router.get("/top-rated")
def top_rated_movies(
    db: Session = Depends(get_db)
):

    from sqlalchemy import func

    movies = (
        db.query(
            Movie.movie_id,
            Movie.title,
            Movie.genres,
            Movie.release_year,
            Movie.poster_url,
            Movie.backdrop_url,
            func.avg(
                # Ratings table is intentionally imported here
                # to avoid changing your existing model structure
                __import__("models").Rating.rating
            ).label("rating")
        )
        .join(
            __import__("models").Rating,
            Movie.movie_id ==
            __import__("models").Rating.movie_id
        )
        .group_by(
            Movie.movie_id,
            Movie.title,
            Movie.genres,
            Movie.release_year,
            Movie.poster_url,
            Movie.backdrop_url
        )
        .order_by(
            func.avg(
                __import__("models").Rating.rating
            ).desc()
        )
        .limit(10)
        .all()
    )


    return [
        {
            "movie_id": movie.movie_id,
            "title": movie.title,
            "genres": movie.genres,
            "release_year": movie.release_year,
            "poster_url": movie.poster_url,
            "backdrop_url": movie.backdrop_url,
            "rating": round(
                float(movie.rating), 2
            )
            if movie.rating is not None
            else 0
        }

        for movie in movies
    ]


# ============================================================
# NEW RELEASES FROM TMDB
# ============================================================

@router.get("/new-releases")
def new_releases():

    if not TMDB_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="TMDB API key is not configured."
        )


    try:

        response = tmdb_session.get(
            f"{TMDB_BASE_URL}/movie/now_playing",
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US",
                "region": "IN",
                "page": 1
            },
            timeout=10
        )


        if not response.ok:

            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch new releases from TMDB."
            )


        data = response.json()


        results = []


        for movie in data.get("results", []):

            poster_url = None
            backdrop_url = None


            if movie.get("poster_path"):

                poster_url = (
                    "https://image.tmdb.org/t/p/w500"
                    + movie["poster_path"]
                )


            if movie.get("backdrop_path"):

                backdrop_url = (
                    "https://image.tmdb.org/t/p/w1280"
                    + movie["backdrop_path"]
                )


            results.append({

                "movie_id": None,

                "tmdb_id": movie.get("id"),

                "title": movie.get("title"),

                "overview": movie.get("overview"),

                "release_date":
                    movie.get("release_date"),

                "release_year":
                    (
                        movie.get("release_date", "")[:4]
                        if movie.get("release_date")
                        else None
                    ),

                "rating":
                    movie.get("vote_average"),

                "vote_count":
                    movie.get("vote_count"),

                "poster_url":
                    poster_url,

                "backdrop_url":
                    backdrop_url,

                "source": "tmdb"

            })


        return results


    except HTTPException:

        raise


    except Exception as error:

        print(
            "TMDB new releases error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to fetch new releases."
        )


# ============================================================
# TMDB MOVIE DETAILS + AUTOMATIC MYSQL IMPORT
# ============================================================

@router.get("/tmdb/{tmdb_id}")
def get_tmdb_movie(
    tmdb_id: int,
    db: Session = Depends(get_db)
):

    if not TMDB_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="TMDB API key is not configured."
        )


    # ========================================================
    # STEP 1: CHECK MYSQL FIRST
    # ========================================================

    existing_movie = (
        db.query(Movie)
        .filter(
            Movie.tmdb_id == tmdb_id
        )
        .first()
    )


    # ========================================================
    # STEP 2: GET DETAILS FROM TMDB
    # ========================================================

    try:

        response = tmdb_session.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={
                "api_key": TMDB_API_KEY,
                "language": "en-US"
            },
            timeout=10
        )


        if response.status_code == 404:

            raise HTTPException(
                status_code=404,
                detail="Movie not found on TMDB."
            )


        if not response.ok:

            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch movie from TMDB."
            )


        data = response.json()


    except HTTPException:

        raise


    except Exception as error:

        print(
            "TMDB details error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to connect to TMDB."
        )


    # ========================================================
    # STEP 3: EXTRACT DATA
    # ========================================================

    release_date = data.get(
        "release_date"
    )


    release_year = None


    if release_date:

        release_year = int(
            release_date[:4]
        )


    # --------------------------------------------------------
    # GENRES
    # --------------------------------------------------------

    genres = " | ".join(
        genre["name"]
        for genre in data.get(
            "genres",
            []
        )
    )


    # --------------------------------------------------------
    # POSTER
    # --------------------------------------------------------

    poster_url = None


    if data.get("poster_path"):

        poster_url = (
            "https://image.tmdb.org/t/p/w500"
            + data["poster_path"]
        )


    # --------------------------------------------------------
    # BACKDROP
    # --------------------------------------------------------

    backdrop_url = None


    if data.get("backdrop_path"):

        backdrop_url = (
            "https://image.tmdb.org/t/p/w1280"
            + data["backdrop_path"]
        )


    # ========================================================
    # STEP 4: INSERT INTO MYSQL IF NOT EXISTS
    # ========================================================

    if existing_movie:

        print(
            f"Movie already exists in MySQL: "
            f"{existing_movie.movie_id}"
        )

        movie = existing_movie


    else:

        print(
            f"Adding TMDB movie to MySQL: "
            f"{data.get('title')}"
        )


        movie = Movie(

            title=data.get(
                "title"
            ),

            genres=genres,

            release_year=release_year,

            tmdb_id=tmdb_id,

            poster_url=poster_url,

            backdrop_url=backdrop_url,

            overview=data.get(
                "overview"
            ),

            runtime=data.get(
                "runtime"
            )

        )


        db.add(movie)

        db.commit()

        db.refresh(movie)


        print(
            f"TMDB movie added successfully. "
            f"MySQL movie_id = {movie.movie_id}"
        )


    # ========================================================
    # STEP 5: RETURN MYSQL MOVIE ID
    # ========================================================

    return {

        "movie_id":
            movie.movie_id,

        "tmdb_id":
            movie.tmdb_id,

        "title":
            movie.title,

        "original_title":
            data.get(
                "original_title"
            ),

        "genres":
            movie.genres,

        "release_date":
            release_date,

        "release_year":
            movie.release_year,

        "overview":
            movie.overview,

        "runtime":
            movie.runtime,

        "rating":
            data.get(
                "vote_average"
            ),

        "vote_count":
            data.get(
                "vote_count"
            ),

        "popularity":
            data.get(
                "popularity"
            ),

        "poster_url":
            movie.poster_url,

        "backdrop_url":
            movie.backdrop_url,

        "source":
            "tmdb"

    }


# ============================================================
# GET MOVIE BY MYSQL ID
# ============================================================

@router.get("/{movie_id}")
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):

    movie = (
        db.query(Movie)
        .filter(
            Movie.movie_id == movie_id
        )
        .first()
    )


    if not movie:

        raise HTTPException(
            status_code=404,
            detail="Movie not found."
        )


    return movie