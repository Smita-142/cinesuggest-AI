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

        # Add watch history
        connection.execute(
            text("""
                INSERT INTO watch_history
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
            "message": "Movie added to watch history",
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

        result = connection.execute(
            text("""
                SELECT
                    wh.id,
                    wh.user_id,
                    wh.movie_id,
                    m.title,
                    m.genres,
                    m.poster_url,
                    wh.watched_at
                FROM watch_history wh
                JOIN movies m
                    ON wh.movie_id = m.movie_id
                WHERE wh.user_id = :user_id
                ORDER BY wh.watched_at DESC
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