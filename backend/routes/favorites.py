from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from database import engine

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


# Request body for adding a favorite
class FavoriteRequest(BaseModel):
    user_id: int
    movie_id: int


# --------------------------------------------------
# ADD FAVORITE
# POST /favorites/
# --------------------------------------------------

@router.post("/")
def add_favorite(data: FavoriteRequest):

    with engine.begin() as connection:

        # Check whether user exists
        user = connection.execute(
            text("""
                SELECT id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": data.user_id
            }
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Check whether movie exists
        movie = connection.execute(
            text("""
                SELECT movie_id
                FROM movies
                WHERE movie_id = :movie_id
            """),
            {
                "movie_id": data.movie_id
            }
        ).fetchone()

        if not movie:
            raise HTTPException(
                status_code=404,
                detail="Movie not found"
            )

        # Check whether already in favorites
        existing = connection.execute(
            text("""
                SELECT id
                FROM favorites
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": data.user_id,
                "movie_id": data.movie_id
            }
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Movie is already in favorites"
            )

        # Insert favorite
        connection.execute(
            text("""
                INSERT INTO favorites
                (user_id, movie_id)
                VALUES
                (:user_id, :movie_id)
            """),
            {
                "user_id": data.user_id,
                "movie_id": data.movie_id
            }
        )

        return {
            "message": "Movie added to favorites",
            "user_id": data.user_id,
            "movie_id": data.movie_id
        }


# --------------------------------------------------
# GET USER FAVORITES
# GET /favorites/user/{user_id}
# --------------------------------------------------

@router.get("/user/{user_id}")
def get_user_favorites(user_id: int):

    with engine.connect() as connection:

        # Check whether user exists
        user = connection.execute(
            text("""
                SELECT id
                FROM users
                WHERE id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Get favorite movies
        result = connection.execute(
            text("""
                SELECT
                    f.id,
                    f.user_id,
                    f.movie_id,
                    m.title,
                    m.genres,
                    m.poster_url,
                    f.created_at
                FROM favorites f
                JOIN movies m
                    ON f.movie_id = m.movie_id
                WHERE f.user_id = :user_id
                ORDER BY f.created_at DESC
            """),
            {
                "user_id": user_id
            }
        )

        favorites = result.mappings().all()

        return {
            "user_id": user_id,
            "favorites": favorites
        }


# --------------------------------------------------
# CHECK WHETHER MOVIE IS FAVORITE
# GET /favorites/check/{user_id}/{movie_id}
# --------------------------------------------------

@router.get("/check/{user_id}/{movie_id}")
def check_favorite(
    user_id: int,
    movie_id: int
):

    with engine.connect() as connection:

        favorite = connection.execute(
            text("""
                SELECT id
                FROM favorites
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": user_id,
                "movie_id": movie_id
            }
        ).fetchone()

        if favorite:
            return {
                "user_id": user_id,
                "movie_id": movie_id,
                "is_favorite": True
            }

        return {
            "user_id": user_id,
            "movie_id": movie_id,
            "is_favorite": False
        }


# --------------------------------------------------
# DELETE FAVORITE
# DELETE /favorites/{user_id}/{movie_id}
# --------------------------------------------------

@router.delete("/{user_id}/{movie_id}")
def delete_favorite(
    user_id: int,
    movie_id: int
):

    with engine.begin() as connection:

        # Check whether favorite exists
        existing = connection.execute(
            text("""
                SELECT id
                FROM favorites
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": user_id,
                "movie_id": movie_id
            }
        ).fetchone()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Favorite not found"
            )

        # Delete favorite
        connection.execute(
            text("""
                DELETE FROM favorites
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": user_id,
                "movie_id": movie_id
            }
        )

        return {
            "message": "Movie removed from favorites",
            "user_id": user_id,
            "movie_id": movie_id
        }