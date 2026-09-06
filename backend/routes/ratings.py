from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from database import engine

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"]
)


class RatingRequest(BaseModel):
    user_id: int
    movie_id: int
    rating: float


@router.post("/")
def add_rating(data: RatingRequest):

    # Check rating value
    if data.rating < 0.5 or data.rating > 5.0:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 0.5 and 5.0"
        )

    with engine.begin() as connection:

        # Check user exists
        user = connection.execute(
            text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": data.user_id}
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Check movie exists
        movie = connection.execute(
            text("SELECT movie_id FROM movies WHERE movie_id = :movie_id"),
            {"movie_id": data.movie_id}
        ).fetchone()

        if not movie:
            raise HTTPException(
                status_code=404,
                detail="Movie not found"
            )

        # Check whether user already rated this movie
        existing = connection.execute(
            text("""
                SELECT id
                FROM user_ratings
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": data.user_id,
                "movie_id": data.movie_id
            }
        ).fetchone()

        if existing:

            # Update existing rating
            connection.execute(
                text("""
                    UPDATE user_ratings
                    SET rating = :rating,
                        rated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id
                    AND movie_id = :movie_id
                """),
                {
                    "rating": data.rating,
                    "user_id": data.user_id,
                    "movie_id": data.movie_id
                }
            )

            return {
                "message": "Rating updated successfully",
                "user_id": data.user_id,
                "movie_id": data.movie_id,
                "rating": data.rating
            }

        # Add new rating
        connection.execute(
            text("""
                INSERT INTO user_ratings
                (user_id, movie_id, rating)
                VALUES
                (:user_id, :movie_id, :rating)
            """),
            {
                "user_id": data.user_id,
                "movie_id": data.movie_id,
                "rating": data.rating
            }
        )

        return {
            "message": "Rating added successfully",
            "user_id": data.user_id,
            "movie_id": data.movie_id,
            "rating": data.rating
        }
@router.get("/user/{user_id}")
def get_user_ratings(user_id: int):
            with engine.connect() as connection:

                result = connection.execute(
                    text("""
                        SELECT
                            ur.id,
                            ur.user_id,
                            ur.movie_id,
                            m.title,
                            ur.rating,
                            ur.rated_at
                        FROM user_ratings ur
                        JOIN movies m
                            ON ur.movie_id = m.movie_id
                        WHERE ur.user_id = :user_id
                        ORDER BY ur.rated_at DESC
                    """),
                    {"user_id": user_id}
                )

                ratings = result.mappings().all()

                if not ratings:
                    return {
                        "message": "No ratings found",
                        "user_id": user_id,
                        "ratings": []
                    }

                return {
                    "user_id": user_id,
                    "ratings": ratings
                }
@router.put("/{user_id}/{movie_id}")
def update_rating(
    user_id: int,
    movie_id: int,
    rating: float
):

    if rating < 0.5 or rating > 5.0:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 0.5 and 5.0"
        )

    with engine.begin() as connection:

        existing = connection.execute(
            text("""
                SELECT id
                FROM user_ratings
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
                detail="Rating not found"
            )

        connection.execute(
            text("""
                UPDATE user_ratings
                SET rating = :rating,
                    rated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "rating": rating,
                "user_id": user_id,
                "movie_id": movie_id
            }
        )

        return {
            "message": "Rating updated successfully",
            "user_id": user_id,
            "movie_id": movie_id,
            "rating": rating
        }
@router.delete("/{user_id}/{movie_id}")
def delete_rating(
    user_id: int,
    movie_id: int
):

    with engine.begin() as connection:

        existing = connection.execute(
            text("""
                SELECT id
                FROM user_ratings
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
                detail="Rating not found"
            )

        connection.execute(
            text("""
                DELETE FROM user_ratings
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": user_id,
                "movie_id": movie_id
            }
        )

        return {
            "message": "Rating deleted successfully",
            "user_id": user_id,
            "movie_id": movie_id
        }