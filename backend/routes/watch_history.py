from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from database import engine

router = APIRouter(
    prefix="/watch-history",
    tags=["Watch History"]
)


class WatchHistoryRequest(BaseModel):
    user_id: int
    movie_id: int


# --------------------------------------------------
# ADD WATCH HISTORY
# POST /watch-history/
# --------------------------------------------------

@router.post("/")
def add_watch_history(data: WatchHistoryRequest):

    with engine.begin() as connection:

        # Check user exists
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

        # Check movie exists
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

        # Check if movie already exists in watch history for this user
        existing = connection.execute(
            text("""
                SELECT id
                FROM watch_history
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": data.user_id,
                "movie_id": data.movie_id
            }
        ).fetchone()

        if existing:
            # Update timestamp to bring to top of history without duplicating
            connection.execute(
                text("""
                    UPDATE watch_history
                    SET watched_at = NOW()
                    WHERE id = :id
                """),
                {"id": existing[0]}
            )
            message = "Watch history timestamp updated"
        else:
            # Add new watch history entry
            connection.execute(
                text("""
                    INSERT INTO watch_history
                    (user_id, movie_id, watched_at)
                    VALUES
                    (:user_id, :movie_id, NOW())
                """),
                {
                    "user_id": data.user_id,
                    "movie_id": data.movie_id
                }
            )
            message = "Movie added to watch history"

        return {
            "message": message,
            "user_id": data.user_id,
            "movie_id": data.movie_id
        }


# --------------------------------------------------
# GET USER WATCH HISTORY
# GET /watch-history/user/{user_id}
# --------------------------------------------------

@router.get("/user/{user_id}")
def get_watch_history(user_id: int):

    with engine.connect() as connection:

        # Check user exists
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

        # Select unique movies with the most recent watched_at timestamp
        result = connection.execute(
            text("""
                SELECT
                    latest.max_id AS id,
                    latest.user_id,
                    latest.movie_id,
                    m.title,
                    m.genres,
                    m.poster_url,
                    latest.max_watched AS watched_at
                FROM (
                    SELECT
                        user_id,
                        movie_id,
                        MAX(id) AS max_id,
                        MAX(watched_at) AS max_watched
                    FROM watch_history
                    WHERE user_id = :user_id
                    GROUP BY user_id, movie_id
                ) latest
                JOIN movies m
                    ON latest.movie_id = m.movie_id
                ORDER BY latest.max_watched DESC
            """),
            {
                "user_id": user_id
            }
        )

        history = result.mappings().all()

        return {
            "user_id": user_id,
            "watch_history": history
        }


# --------------------------------------------------
# DELETE WATCH HISTORY ENTRY
# DELETE /watch-history/{user_id}/{movie_id}
# --------------------------------------------------

@router.delete("/{user_id}/{movie_id}")
def delete_watch_history(
    user_id: int,
    movie_id: int
):

    with engine.begin() as connection:

        existing = connection.execute(
            text("""
                SELECT id
                FROM watch_history
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
                detail="Watch history not found"
            )

        connection.execute(
            text("""
                DELETE FROM watch_history
                WHERE user_id = :user_id
                AND movie_id = :movie_id
            """),
            {
                "user_id": user_id,
                "movie_id": movie_id
            }
        )

        return {
            "message": "Movie removed from watch history",
            "user_id": user_id,
            "movie_id": movie_id
        }