import pandas as pd
import joblib
import os

from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_PATH = os.path.join(BASE_DIR, "movies.csv")
RATINGS_PATH = os.path.join(BASE_DIR, "ratings.csv.csv")
SVD_PATH = os.path.join(BASE_DIR, "svd_model.pkl")


# =========================================================
# LOAD DATA
# =========================================================

movies = pd.read_csv("C:/Users/khush/OneDrive/Desktop/New folder (2)/CineMatch-AI/backend/ml/movies.csv")
ratings = pd.read_csv("C:/Users/khush/OneDrive/Desktop/New folder (2)/CineMatch-AI/backend/ml/ratings.csv.csv")

print("Movies loaded:", len(movies))
print("Ratings loaded:", len(ratings))


# =========================================================
# LOAD TRAINED SVD MODEL
# =========================================================

svd_model = joblib.load(SVD_PATH)

print("SVD model loaded successfully!")
print("Model type:", type(svd_model))


# =========================================================
# USER-ITEM MATRIX
# Used for User-Based Collaborative Filtering
# =========================================================

user_item_matrix = ratings.pivot_table(
    index="userId",
    columns="movieId",
    values="rating"
)

user_item_matrix_filled = user_item_matrix.fillna(0)

print(
    "User-Item Matrix shape:",
    user_item_matrix_filled.shape
)


# =========================================================
# 1. USER-BASED COLLABORATIVE FILTERING
# =========================================================

def get_user_based_recommendations(user_id, n=10):

    # -----------------------------------------------------
    # Check whether user exists
    # -----------------------------------------------------

    if user_id not in user_item_matrix_filled.index:

        raise ValueError(
            f"User {user_id} does not exist in "
            "MovieLens ratings."
        )


    # -----------------------------------------------------
    # Find target user's rating vector
    # -----------------------------------------------------

    target_user = user_item_matrix_filled.loc[
        [user_id]
    ]


    # -----------------------------------------------------
    # Calculate cosine similarity
    # -----------------------------------------------------

    similarities = cosine_similarity(
        target_user,
        user_item_matrix_filled
    )[0]


    # -----------------------------------------------------
    # Create similarity DataFrame
    # -----------------------------------------------------

    similarity_df = pd.DataFrame({
        "userId": user_item_matrix_filled.index,
        "similarity": similarities
    })


    # -----------------------------------------------------
    # Remove target user
    # -----------------------------------------------------

    similarity_df = similarity_df[
        similarity_df["userId"] != user_id
    ]


    # -----------------------------------------------------
    # Select top 5 similar users
    # -----------------------------------------------------

    similar_users = similarity_df.sort_values(
        "similarity",
        ascending=False
    ).head(5)


    # -----------------------------------------------------
    # Get ratings from similar users
    # -----------------------------------------------------

    similar_user_ratings = ratings[
        ratings["userId"].isin(
            similar_users["userId"]
        )
    ].copy()


    # -----------------------------------------------------
    # Add similarity score
    # -----------------------------------------------------

    similar_user_ratings = (
        similar_user_ratings
        .merge(
            similar_users,
            on="userId"
        )
    )


    # -----------------------------------------------------
    # Calculate weighted rating
    # -----------------------------------------------------

    similar_user_ratings[
        "weighted_score"
    ] = (
        similar_user_ratings["rating"]
        * similar_user_ratings["similarity"]
    )


    # -----------------------------------------------------
    # Movies already rated by target user
    # -----------------------------------------------------

    user_rated_movies = ratings[
        ratings["userId"] == user_id
    ]["movieId"].tolist()


    # -----------------------------------------------------
    # Remove already rated movies
    # -----------------------------------------------------

    unseen_movies = similar_user_ratings[
        ~similar_user_ratings["movieId"].isin(
            user_rated_movies
        )
    ]


    # -----------------------------------------------------
    # Calculate total score for each movie
    # -----------------------------------------------------

    user_scores = (
        unseen_movies
        .groupby("movieId")[
            "weighted_score"
        ]
        .sum()
        .reset_index()
    )


    if len(user_scores) == 0:

        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "user_score"
            ]
        )


    # -----------------------------------------------------
    # Normalize score to 0-100
    # -----------------------------------------------------

    max_score = user_scores[
        "weighted_score"
    ].max()

    if max_score > 0:

        user_scores["user_score"] = (
            user_scores["weighted_score"]
            / max_score
        ) * 100

    else:

        user_scores["user_score"] = 0


    # -----------------------------------------------------
    # Add movie information
    # -----------------------------------------------------

    user_scores = user_scores.merge(
        movies[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )


    # -----------------------------------------------------
    # Sort recommendations
    # -----------------------------------------------------

    user_scores = user_scores.sort_values(
        "user_score",
        ascending=False
    )


    return user_scores.head(n)[
        [
            "movieId",
            "title",
            "genres",
            "user_score"
        ]
    ]


# =========================================================
# 2. ITEM-BASED COLLABORATIVE FILTERING
# =========================================================

def get_item_based_recommendations(user_id, n=10):

    # -----------------------------------------------------
    # Get movies rated by user
    # -----------------------------------------------------

    user_movies = ratings[
        ratings["userId"] == user_id
    ][
        [
            "movieId",
            "rating"
        ]
    ]


    if len(user_movies) == 0:

        raise ValueError(
            f"User {user_id} has no ratings."
        )


    # -----------------------------------------------------
    # Create Movie-User Matrix
    # -----------------------------------------------------

    movie_user_matrix = ratings.pivot_table(
        index="movieId",
        columns="userId",
        values="rating"
    )

    movie_user_matrix_filled = (
        movie_user_matrix.fillna(0)
    )


    # -----------------------------------------------------
    # Movies already rated
    # -----------------------------------------------------

    user_rated_movies = user_movies[
        "movieId"
    ].tolist()


    item_recommendations = []


    # -----------------------------------------------------
    # Compare each movie rated by user
    # with other movies
    # -----------------------------------------------------

    for _, row in user_movies.iterrows():

        movie_id = row["movieId"]

        user_rating = row["rating"]


        # Movie must exist in matrix

        if (
            movie_id
            not in movie_user_matrix_filled.index
        ):
            continue


        # -------------------------------------------------
        # Get target movie vector
        # -------------------------------------------------

        target_movie = (
            movie_user_matrix_filled.loc[
                [movie_id]
            ]
        )


        # -------------------------------------------------
        # Calculate cosine similarity
        # -------------------------------------------------

        similarities = cosine_similarity(
            target_movie,
            movie_user_matrix_filled
        )[0]


        # -------------------------------------------------
        # Create similarity DataFrame
        # -------------------------------------------------

        similarity_df = pd.DataFrame({
            "movieId":
                movie_user_matrix_filled.index,
            "similarity":
                similarities
        })


        # -------------------------------------------------
        # Remove same movie
        # -------------------------------------------------

        similarity_df = similarity_df[
            similarity_df["movieId"] != movie_id
        ]


        # -------------------------------------------------
        # Get top 20 similar movies
        # -------------------------------------------------

        similarity_df = (
            similarity_df
            .sort_values(
                "similarity",
                ascending=False
            )
            .head(20)
        )


        # -------------------------------------------------
        # Calculate weighted score
        # -------------------------------------------------

        for _, similar_movie in (
            similarity_df.iterrows()
        ):

            similar_movie_id = int(
                similar_movie["movieId"]
            )

            similarity = (
                similar_movie["similarity"]
            )


            weighted_score = (
                user_rating
                * similarity
            )


            item_recommendations.append({
                "movieId":
                    similar_movie_id,

                "weighted_score":
                    weighted_score
            })


    # -----------------------------------------------------
    # Check recommendations
    # -----------------------------------------------------

    if not item_recommendations:

        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "item_score"
            ]
        )


    # -----------------------------------------------------
    # Convert to DataFrame
    # -----------------------------------------------------

    item_scores = pd.DataFrame(
        item_recommendations
    )


    # -----------------------------------------------------
    # Remove movies already rated
    # -----------------------------------------------------

    item_scores = item_scores[
        ~item_scores["movieId"].isin(
            user_rated_movies
        )
    ]


    # -----------------------------------------------------
    # Combine duplicate movie scores
    # -----------------------------------------------------

    item_scores = (
        item_scores
        .groupby("movieId")[
            "weighted_score"
        ]
        .sum()
        .reset_index()
    )


    if len(item_scores) == 0:

        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "item_score"
            ]
        )


    # -----------------------------------------------------
    # Normalize to 0-100
    # -----------------------------------------------------

    max_score = item_scores[
        "weighted_score"
    ].max()

    if max_score > 0:

        item_scores["item_score"] = (
            item_scores["weighted_score"]
            / max_score
        ) * 100

    else:

        item_scores["item_score"] = 0


    # -----------------------------------------------------
    # Add movie information
    # -----------------------------------------------------

    item_scores = item_scores.merge(
        movies[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )


    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    item_scores = item_scores.sort_values(
        "item_score",
        ascending=False
    )


    return item_scores.head(n)[
        [
            "movieId",
            "title",
            "genres",
            "item_score"
        ]
    ]


# =========================================================
# 3. SVD RECOMMENDATIONS
# =========================================================

def get_svd_recommendations(user_id, n=10):

    # -----------------------------------------------------
    # Check user exists
    # -----------------------------------------------------

    if user_id not in ratings[
        "userId"
    ].unique():

        raise ValueError(
            f"User {user_id} does not exist in "
            "MovieLens ratings."
        )


    # -----------------------------------------------------
    # Get movies already rated
    # -----------------------------------------------------

    user_rated_movies = ratings[
        ratings["userId"] == user_id
    ]["movieId"].tolist()


    # -----------------------------------------------------
    # Get all movies
    # -----------------------------------------------------

    all_movie_ids = movies[
        "movieId"
    ].unique()


    recommendations = []


    # -----------------------------------------------------
    # Predict rating for every unseen movie
    # -----------------------------------------------------

    for movie_id in all_movie_ids:

        if movie_id in user_rated_movies:
            continue


        prediction = svd_model.predict(
            user_id,
            int(movie_id)
        )


        recommendations.append({
            "movieId":
                int(movie_id),

            "predicted_rating":
                prediction.est
        })


    # -----------------------------------------------------
    # Convert to DataFrame
    # -----------------------------------------------------

    svd_scores = pd.DataFrame(
        recommendations
    )


    if len(svd_scores) == 0:

        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "predicted_rating",
                "svd_score"
            ]
        )


    # -----------------------------------------------------
    # Normalize predicted rating to 0-100
    # -----------------------------------------------------

    min_rating = svd_scores[
        "predicted_rating"
    ].min()

    max_rating = svd_scores[
        "predicted_rating"
    ].max()


    if max_rating > min_rating:

        svd_scores["svd_score"] = (
            (
                svd_scores["predicted_rating"]
                - min_rating
            )
            /
            (
                max_rating
                - min_rating
            )
        ) * 100

    else:

        svd_scores["svd_score"] = 100


    # -----------------------------------------------------
    # Add movie information
    # -----------------------------------------------------

    svd_scores = svd_scores.merge(
        movies[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )


    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    svd_scores = svd_scores.sort_values(
        "predicted_rating",
        ascending=False
    )


    return svd_scores.head(n)[
        [
            "movieId",
            "title",
            "genres",
            "predicted_rating",
            "svd_score"
        ]
    ]


# =========================================================
# 4. HYBRID RECOMMENDATIONS
# =========================================================

def get_hybrid_recommendations(user_id, n=10):

    # -----------------------------------------------------
    # Get User-Based CF scores
    # -----------------------------------------------------

    user_scores = get_user_based_recommendations(
        user_id,
        n=len(movies)
    )


    # -----------------------------------------------------
    # Get Item-Based CF scores
    # -----------------------------------------------------

    item_scores = get_item_based_recommendations(
        user_id,
        n=len(movies)
    )


    # -----------------------------------------------------
    # Get SVD scores
    # -----------------------------------------------------

    svd_scores = get_svd_recommendations(
        user_id,
        n=len(movies)
    )


    # -----------------------------------------------------
    # Keep only required columns
    # -----------------------------------------------------

    user_scores = user_scores[
        [
            "movieId",
            "user_score"
        ]
    ]

    item_scores = item_scores[
        [
            "movieId",
            "item_score"
        ]
    ]

    svd_scores = svd_scores[
        [
            "movieId",
            "svd_score"
        ]
    ]


    # -----------------------------------------------------
    # Merge User CF + Item CF
    # -----------------------------------------------------

    hybrid = pd.merge(
        user_scores,
        item_scores,
        on="movieId",
        how="outer"
    )


    # -----------------------------------------------------
    # Merge SVD
    # -----------------------------------------------------

    hybrid = pd.merge(
        hybrid,
        svd_scores,
        on="movieId",
        how="outer"
    )


    # -----------------------------------------------------
    # Missing scores = 0
    # -----------------------------------------------------

    hybrid["user_score"] = (
        hybrid["user_score"]
        .fillna(0)
    )

    hybrid["item_score"] = (
        hybrid["item_score"]
        .fillna(0)
    )

    hybrid["svd_score"] = (
        hybrid["svd_score"]
        .fillna(0)
    )


    # =====================================================
    # HYBRID FORMULA
    # =====================================================

    hybrid["hybrid_score"] = (
        0.30 * hybrid["user_score"]
        + 0.30 * hybrid["item_score"]
        + 0.40 * hybrid["svd_score"]
    )


    # -----------------------------------------------------
    # Remove already rated movies
    # -----------------------------------------------------

    user_rated_movies = ratings[
        ratings["userId"] == user_id
    ]["movieId"].tolist()


    hybrid = hybrid[
        ~hybrid["movieId"].isin(
            user_rated_movies
        )
    ]


    # -----------------------------------------------------
    # Add movie details
    # -----------------------------------------------------

    hybrid = hybrid.merge(
        movies[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )


    # -----------------------------------------------------
    # Sort by hybrid score
    # -----------------------------------------------------

    hybrid = hybrid.sort_values(
        "hybrid_score",
        ascending=False
    )


    # -----------------------------------------------------
    # Get Top N
    # -----------------------------------------------------

    hybrid = hybrid.head(n).copy()


    # -----------------------------------------------------
    # Match percentage
    # -----------------------------------------------------

    hybrid["match_percentage"] = (
        hybrid["hybrid_score"]
        .round(2)
    )


    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return hybrid[
        [
            "movieId",
            "title",
            "genres",
            "user_score",
            "item_score",
            "svd_score",
            "hybrid_score",
            "match_percentage"
        ]
        
    ]
    # =========================================================
# 5. NEW USER RECOMMENDATIONS
# Uses ratings from MySQL user_ratings
# =========================================================

def get_new_user_recommendations(
    user_ratings,
    n=10
):
    """
    Generate recommendations for a new application user.

    user_ratings must be a list of dictionaries like:

    [
        {"movieId": 1, "rating": 5.0},
        {"movieId": 5349, "rating": 3.0}
    ]
    """

    if not user_ratings:
        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "recommendation_score"
            ]
        )

    # -----------------------------------------------------
    # Convert user's ratings to DataFrame
    # -----------------------------------------------------

    new_user_ratings = pd.DataFrame(user_ratings)

    new_user_ratings["movieId"] = (
        new_user_ratings["movieId"].astype(int)
    )

    new_user_ratings["rating"] = (
        new_user_ratings["rating"].astype(float)
    )

    # -----------------------------------------------------
    # Movie-user matrix from MovieLens
    # -----------------------------------------------------

    movie_user_matrix = ratings.pivot_table(
        index="movieId",
        columns="userId",
        values="rating"
    ).fillna(0)

    # -----------------------------------------------------
    # Movies already rated by new user
    # -----------------------------------------------------

    rated_movie_ids = (
        new_user_ratings["movieId"]
        .tolist()
    )

    recommendations = []

    # -----------------------------------------------------
    # Compare each movie rated by new user
    # with MovieLens movies
    # -----------------------------------------------------

    for _, row in new_user_ratings.iterrows():

        movie_id = int(row["movieId"])
        user_rating = float(row["rating"])

        # Movie must exist in MovieLens dataset

        if movie_id not in movie_user_matrix.index:
            continue

        target_movie = movie_user_matrix.loc[
            [movie_id]
        ]

        similarities = cosine_similarity(
            target_movie,
            movie_user_matrix
        )[0]

        similarity_df = pd.DataFrame({
            "movieId": movie_user_matrix.index,
            "similarity": similarities
        })

        # Remove the same movie

        similarity_df = similarity_df[
            similarity_df["movieId"] != movie_id
        ]

        # Keep strongest similarities

        similarity_df = (
            similarity_df
            .sort_values(
                "similarity",
                ascending=False
            )
            .head(50)
        )

        # -------------------------------------------------
        # Weight similarity by user's rating
        # -------------------------------------------------

        for _, similar_movie in (
            similarity_df.iterrows()
        ):

            similar_movie_id = int(
                similar_movie["movieId"]
            )

            similarity = float(
                similar_movie["similarity"]
            )

            # Only positive user preferences
            # should strongly influence recommendations

            rating_weight = user_rating / 5.0

            score = (
                similarity
                * rating_weight
            )

            recommendations.append({
                "movieId": similar_movie_id,
                "score": score
            })

    # -----------------------------------------------------
    # No recommendations
    # -----------------------------------------------------

    if not recommendations:

        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "recommendation_score"
            ]
        )

    # -----------------------------------------------------
    # Convert to DataFrame
    # -----------------------------------------------------

    recommendation_df = pd.DataFrame(
        recommendations
    )

    # -----------------------------------------------------
    # Remove movies already rated
    # -----------------------------------------------------

    recommendation_df = recommendation_df[
        ~recommendation_df["movieId"].isin(
            rated_movie_ids
        )
    ]

    # -----------------------------------------------------
    # Combine duplicate movie recommendations
    # -----------------------------------------------------

    recommendation_df = (
        recommendation_df
        .groupby("movieId")["score"]
        .sum()
        .reset_index()
    )

    if recommendation_df.empty:

        return pd.DataFrame(
            columns=[
                "movieId",
                "title",
                "genres",
                "recommendation_score"
            ]
        )

    # -----------------------------------------------------
    # Normalize score to 0-100
    # -----------------------------------------------------

    max_score = recommendation_df["score"].max()

    if max_score > 0:

        recommendation_df[
            "recommendation_score"
        ] = (
            recommendation_df["score"]
            / max_score
        ) * 100

    else:

        recommendation_df[
            "recommendation_score"
        ] = 0

    # -----------------------------------------------------
    # Add movie information
    # -----------------------------------------------------

    recommendation_df = recommendation_df.merge(
        movies[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )

    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    recommendation_df = (
        recommendation_df
        .sort_values(
            "recommendation_score",
            ascending=False
        )
    )

    return recommendation_df.head(n)[
        [
            "movieId",
            "title",
            "genres",
            "recommendation_score"
        ]
    ]