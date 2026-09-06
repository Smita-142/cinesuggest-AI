from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

from ml.recommender import (
    get_hybrid_recommendations,
    get_new_user_recommendations
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/{user_id}")
def get_recommendations(
    user_id: int,
    n: int = 10,
    db: Session = Depends(get_db)
):

    # ---------------------------------------------------------
    # 1. Validate number of recommendations
    # ---------------------------------------------------------

    if n < 1 or n > 50:
        raise HTTPException(
            status_code=400,
            detail="n must be between 1 and 50"
        )


    # ---------------------------------------------------------
    # 2. Get ML user ID
    # ---------------------------------------------------------

    mapping = db.execute(
        text("""
            SELECT ml_user_id
            FROM user_ml_mapping
            WHERE user_id = :user_id
        """),
        {
            "user_id": user_id
        }
    ).fetchone()


    if not mapping:
        raise HTTPException(
            status_code=404,
            detail="ML profile not found for this user."
        )


    ml_user_id = mapping[0]


    try:

        # =====================================================
        # 3. NEW USER
        # =====================================================
        # MovieLens contains users 1-610.
        #
        # New application users start from 611.
        #
        # Their ratings are stored in MySQL user_ratings.
        # =====================================================

        if ml_user_id > 610:

            result = db.execute(
                text("""
                    SELECT
                        movie_id,
                        rating
                    FROM user_ratings
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id
                }
            )

            user_ratings = result.mappings().all()


            # -------------------------------------------------
            # No ratings yet
            # -------------------------------------------------

            if not user_ratings:

                return {
                    "user_id": user_id,
                    "ml_user_id": ml_user_id,
                    "count": 0,
                    "message": "Rate some movies to get recommendations.",
                    "recommendations": []
                }


            # -------------------------------------------------
            # Convert database result into recommender format
            # -------------------------------------------------

            rating_data = [
                {
                    "movieId": int(row["movie_id"]),
                    "rating": float(row["rating"])
                }
                for row in user_ratings
            ]


            # -------------------------------------------------
            # Generate recommendations
            # -------------------------------------------------

            recommendations = get_new_user_recommendations(
                rating_data,
                n
            )


            recommendation_list = (
                recommendations.to_dict(
                    orient="records"
                )
            )


            # -------------------------------------------------
            # Get movie IDs
            # -------------------------------------------------

            movie_ids = [
                int(movie["movieId"])
                for movie in recommendation_list
            ]


            if not movie_ids:

                return {
                    "user_id": user_id,
                    "ml_user_id": ml_user_id,
                    "count": 0,
                    "recommendations": []
                }


            # -------------------------------------------------
            # Get full movie information from MySQL
            # -------------------------------------------------

            placeholders = ", ".join(
                [
                    f":movie_id_{i}"
                    for i in range(len(movie_ids))
                ]
            )


            params = {
                f"movie_id_{i}": movie_id
                for i, movie_id in enumerate(movie_ids)
            }


            result = db.execute(
                text(f"""
                    SELECT
                        movie_id,
                        title,
                        genres,
                        release_year,
                        tmdb_id,
                        poster_url,
                        backdrop_url,
                        overview,
                        runtime
                    FROM movies
                    WHERE movie_id IN ({placeholders})
                """),
                params
            )


            movie_details = result.mappings().all()


            movie_lookup = {
                movie["movie_id"]: dict(movie)
                for movie in movie_details
            }


            # -------------------------------------------------
            # Build final response
            # -------------------------------------------------

            final_recommendations = []


            for recommendation in recommendation_list:

                movie_id = int(
                    recommendation["movieId"]
                )


                movie = movie_lookup.get(movie_id)


                if not movie:
                    continue


                final_recommendations.append({

                    "movie_id": movie_id,

                    "title": movie["title"],

                    "genres": movie["genres"],

                    "release_year": movie["release_year"],

                    "tmdb_id": movie["tmdb_id"],

                    "poster_url": movie["poster_url"],

                    "backdrop_url": movie["backdrop_url"],

                    "overview": movie["overview"],

                    "runtime": movie["runtime"],

                    "recommendation_score":
                        recommendation.get(
                            "recommendation_score"
                        )
                })


            return {

                "user_id": user_id,

                "ml_user_id": ml_user_id,

                "count": len(
                    final_recommendations
                ),

                "recommendations":
                    final_recommendations
            }


        # =====================================================
        # 4. EXISTING MOVIELENS USER
        # =====================================================
        # Users 1-610 already exist in MovieLens.
        # Use the original hybrid recommendation system.
        # =====================================================

        recommendations = get_hybrid_recommendations(
            ml_user_id,
            n
        )


        recommendation_list = (
            recommendations.to_dict(
                orient="records"
            )
        )


        movie_ids = [
            int(movie["movieId"])
            for movie in recommendation_list
        ]


        if not movie_ids:

            return {
                "user_id": user_id,
                "ml_user_id": ml_user_id,
                "count": 0,
                "recommendations": []
            }


        # -----------------------------------------------------
        # Get movie details from MySQL
        # -----------------------------------------------------

        placeholders = ", ".join(
            [
                f":movie_id_{i}"
                for i in range(len(movie_ids))
            ]
        )


        params = {
            f"movie_id_{i}": movie_id
            for i, movie_id in enumerate(movie_ids)
        }


        result = db.execute(
            text(f"""
                SELECT
                    movie_id,
                    title,
                    genres,
                    release_year,
                    tmdb_id,
                    poster_url,
                    backdrop_url,
                    overview,
                    runtime
                FROM movies
                WHERE movie_id IN ({placeholders})
            """),
            params
        )


        movie_details = result.mappings().all()


        movie_lookup = {
            movie["movie_id"]: dict(movie)
            for movie in movie_details
        }


        # -----------------------------------------------------
        # Build final recommendations
        # -----------------------------------------------------

        final_recommendations = []


        for recommendation in recommendation_list:

            movie_id = int(
                recommendation["movieId"]
            )


            movie = movie_lookup.get(movie_id)


            if not movie:
                continue


            final_recommendations.append({

                "movie_id": movie_id,

                "title": movie["title"],

                "genres": movie["genres"],

                "release_year": movie["release_year"],

                "tmdb_id": movie["tmdb_id"],

                "poster_url": movie["poster_url"],

                "backdrop_url": movie["backdrop_url"],

                "overview": movie["overview"],

                "runtime": movie["runtime"],

                "user_score":
                    recommendation.get(
                        "user_score"
                    ),

                "item_score":
                    recommendation.get(
                        "item_score"
                    ),

                "svd_score":
                    recommendation.get(
                        "svd_score"
                    ),

                "hybrid_score":
                    recommendation.get(
                        "hybrid_score"
                    ),

                "match_percentage":
                    recommendation.get(
                        "match_percentage"
                    )
            })


        return {

            "user_id": user_id,

            "ml_user_id": ml_user_id,

            "count": len(
                final_recommendations
            ),

            "recommendations":
                final_recommendations
        }


    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )