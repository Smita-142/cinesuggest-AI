import "./MovieDetails.css";
import { useEffect, useState, useRef } from "react";
import { Link, useParams } from "react-router-dom";
import { API_BASE_URL } from "../config/api";

function MovieDetails() {

  const { id, tmdbId } = useParams();

  // ==================================================
  // MOVIE SOURCE
  // ==================================================

  const isTMDBMovie = Boolean(tmdbId);


  // ==================================================
  // MOVIE STATE
  // ==================================================

  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // ==================================================
  // MY LIST STATE
  // ==================================================

  const [isSaved, setIsSaved] = useState(false);


  // ==================================================
  // RATING STATE
  // ==================================================

  const [userRating, setUserRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [ratingLoading, setRatingLoading] = useState(false);
  const [ratingMessage, setRatingMessage] = useState("");

  const hasLoggedHistoryRef = useRef(false);


  // ==================================================
  // GET MOVIE
  // ==================================================

  useEffect(() => {

    const fetchMovie = async () => {

      try {

        setLoading(true);
        setError("");

        let url;


        // ------------------------------------------------
        // TMDB MOVIE
        // ------------------------------------------------

        if (isTMDBMovie) {

          url =
            `${API_BASE_URL}/movies/tmdb/${tmdbId}`;

        }

        // ------------------------------------------------
        // MYSQL MOVIE
        // ------------------------------------------------

        else {

          url =
            `${API_BASE_URL}/movies/${id}`;

        }


        console.log(
          "Fetching movie:",
          url
        );


        const response =
          await fetch(url);


        const data =
          await response.json();


        console.log(
          "Movie from API:",
          data
        );


        if (!response.ok) {

          setError(
            data.detail ||
            "Movie not found"
          );

          return;
        }


        setMovie(data);

      }

      catch (error) {

        console.error(
          "Error fetching movie:",
          error
        );

        setError(
          "Cannot connect to FastAPI server."
        );

      }

      finally {

        setLoading(false);

      }

    };


    fetchMovie();

  }, [id, tmdbId, isTMDBMovie]);


  // ==================================================
  // CHECK FAVORITE
  // ==================================================

  useEffect(() => {

    if (!movie) {
      return;
    }


    // IMPORTANT:
    // Even TMDB movies can now have movie_id
    // because FastAPI automatically imports them.

    if (!movie.movie_id) {
      return;
    }


    const checkFavorite = async () => {

      try {

        const userId =
          localStorage.getItem(
            "user_id"
          );


        if (!userId) {
          return;
        }


        const response =
          await fetch(
            `${API_BASE_URL}/favorites/check/${userId}/${movie.movie_id}`
          );


        const data =
          await response.json();


        console.log(
          "Favorite check:",
          data
        );


        if (!response.ok) {

          console.error(
            data.detail ||
            "Favorite check failed"
          );

          return;
        }


        setIsSaved(
          data.is_favorite
        );

      }

      catch (error) {

        console.error(
          "Error checking favorite:",
          error
        );

      }

    };


    checkFavorite();

  }, [movie]);


  // ==================================================
  // GET USER'S EXISTING RATING
  // ==================================================

  useEffect(() => {

    if (!movie) {
      return;
    }


    if (!movie.movie_id) {
      return;
    }


    const fetchUserRating = async () => {

      try {

        const userId =
          localStorage.getItem(
            "user_id"
          );


        if (!userId) {
          return;
        }


        const response =
          await fetch(
            `${API_BASE_URL}/ratings/user/${userId}`
          );


        const data =
          await response.json();


        console.log(
          "User ratings:",
          data
        );


        if (!response.ok) {
          return;
        }


        const ratings =
          data.ratings || data;


        if (Array.isArray(ratings)) {

          const existingRating =
            ratings.find(
              (rating) =>
                Number(
                  rating.movie_id
                ) === Number(
                  movie.movie_id
                )
            );


          if (existingRating) {

            setUserRating(
              Number(
                existingRating.rating
              )
            );

          }

        }

      }

      catch (error) {

        console.error(
          "Error fetching user rating:",
          error
        );

      }

    };


    fetchUserRating();

  }, [movie]);


  // ==================================================
  // ADD MOVIE TO WATCH HISTORY
  // ==================================================

  useEffect(() => {

    if (!movie || !movie.movie_id) {
      return;
    }

    if (hasLoggedHistoryRef.current) {
      return;
    }

    hasLoggedHistoryRef.current = true;

    const addToWatchHistory = async () => {

      try {

        const userId =
          localStorage.getItem(
            "user_id"
          );


        if (!userId) {

          console.log(
            "No logged-in user."
          );

          return;
        }


        const response =
          await fetch(
            `${API_BASE_URL}/watch-history/`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body: JSON.stringify({

                user_id:
                  Number(userId),

                movie_id:
                  Number(
                    movie.movie_id
                  )

              })

            }
          );


        const data =
          await response.json();


        console.log(
          "Watch history response:",
          data
        );


        if (!response.ok) {

          console.error(
            data.detail ||
            "Failed to add watch history"
          );

        }

      }

      catch (error) {

        console.error(
          "Watch history error:",
          error
        );

      }

    };


    addToWatchHistory();

  }, [movie?.movie_id]);


  // ==================================================
  // SUBMIT RATING
  // ==================================================

  const handleRating = async (rating) => {

    try {

      const userId =
        localStorage.getItem(
          "user_id"
        );


      if (!userId) {

        alert(
          "Please login first."
        );

        return;
      }


      if (!movie) {
        return;
      }


      if (!movie.movie_id) {

        alert(
          "Movie is not available in the database yet."
        );

        return;
      }


      setRatingLoading(true);
      setRatingMessage("");


      const response =
        await fetch(
          `${API_BASE_URL}/ratings/`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

              user_id:
                Number(userId),

              movie_id:
                Number(
                  movie.movie_id
                ),

              rating:
                Number(rating)

            })

          }
        );


      const data =
        await response.json();


      console.log(
        "Rating response:",
        data
      );


      if (!response.ok) {

        setRatingMessage(
          data.detail ||
          "Failed to save rating."
        );

        return;
      }


      setUserRating(
        Number(rating)
      );


      setRatingMessage(
        "Your rating has been saved!"
      );

    }

    catch (error) {

      console.error(
        "Rating error:",
        error
      );


      setRatingMessage(
        "Cannot connect to FastAPI server."
      );

    }

    finally {

      setRatingLoading(false);

    }

  };


  // ==================================================
  // ADD / REMOVE MY LIST
  // ==================================================

  const handleMyList = async () => {

    try {

      const userId =
        localStorage.getItem(
          "user_id"
        );


      if (!userId) {

        alert(
          "Please login first."
        );

        return;
      }


      if (!movie) {
        return;
      }


      if (!movie.movie_id) {

        alert(
          "Movie is not available in the database yet."
        );

        return;
      }


      // =================================================
      // REMOVE
      // =================================================

      if (isSaved) {

        const response =
          await fetch(
            `${API_BASE_URL}/favorites/${userId}/${movie.movie_id}`,
            {
              method: "DELETE"
            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          alert(
            data.detail ||
            "Failed to remove movie"
          );

          return;
        }


        setIsSaved(false);


        alert(
          "Movie removed from My List."
        );

      }


      // =================================================
      // ADD
      // =================================================

      else {

        const response =
          await fetch(
            `${API_BASE_URL}/favorites/`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body: JSON.stringify({

                user_id:
                  Number(userId),

                movie_id:
                  Number(
                    movie.movie_id
                  )

              })

            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          alert(
            data.detail ||
            "Failed to add movie"
          );

          return;
        }


        setIsSaved(true);


        alert(
          "Movie added to My List."
        );

      }

    }

    catch (error) {

      console.error(
        "My List error:",
        error
      );


      alert(
        "Cannot connect to FastAPI server."
      );

    }

  };


  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {

    return (

      <div className="movie-details-page">

        <div className="movie-not-found">

          <h1>
            Loading Movie...
          </h1>

          <p>
            Please wait while movie details
            are loading.
          </p>

        </div>

      </div>

    );

  }


  // ==================================================
  // ERROR
  // ==================================================

  if (error || !movie) {

    return (

      <div className="movie-details-page">

        <div className="movie-not-found">

          <h1>
            Movie Not Found
          </h1>

          <p>
            {error}
          </p>

          <Link to="/home">
            ← Back to Discover
          </Link>

        </div>

      </div>

    );

  }


  // ==================================================
  // GENRES
  // ==================================================

  const genres = movie.genres
    ? movie.genres
        .split("|")
        .map(
          (genre) => genre.trim()
        )
    : [];


  // ==================================================
  // RELEASE YEAR
  // ==================================================

  const releaseYear =
    movie.release_year ||
    (
      movie.release_date
        ? movie.release_date.substring(
            0,
            4
          )
        : ""
    );


  // ==================================================
  // RETURN
  // ==================================================

  return (

    <div className="movie-details-page">


      {/* ==================================================
          NAVBAR
      ================================================== */}

      <nav className="navbar">

        <div className="logo">

          <span>
            🎬
          </span>

          Cinematic AI

        </div>


        <div className="nav-links">

          <Link to="/home">
            Discover
          </Link>

          <Link to="/recommendations">
            My Recommendations
          </Link>

          <Link to="/my-list">
            My List
          </Link>

          <Link to="/history">
            History
          </Link>

        </div>


        <Link
          to="/profile"
          className="profile-circle"
        >
          A
        </Link>

      </nav>


      {/* ==================================================
          MOVIE HERO
      ================================================== */}

      <section className="movie-hero">


        <div className="movie-backdrop">

          <img
            src={
              movie.backdrop_url ||
              movie.poster_url ||
              "/images/default-movie.jpg"
            }
            alt={movie.title}
            onError={(e) => {
              e.currentTarget.onerror = null;
              e.currentTarget.src = "/images/default-movie.jpg";
            }}
          />

        </div>


        <div className="movie-overlay"></div>


        <div className="movie-content">


          {/* POSTER */}

          <div className="movie-poster-large">

            <img
              src={
                movie.poster_url ||
                "/images/default-movie.jpg"
              }
              alt={movie.title}
              onError={(e) => {
                e.currentTarget.onerror = null;
                e.currentTarget.src = "/images/default-movie.jpg";
              }}
            />

          </div>


          {/* MOVIE INFORMATION */}

          <div className="movie-info">


            <p className="movie-label">

              {isTMDBMovie
                ? "TMDB MOVIE"
                : "MOVIE DETAILS"}

            </p>


            <h1>
              {movie.title}
            </h1>


            {/* META */}

            <div className="movie-meta">

              {movie.rating !== undefined &&
                movie.rating !== null && (

                <span className="movie-rating">

                  ★{" "}
                  {Number(
                    movie.rating
                  ).toFixed(1)}

                </span>

              )}


              {releaseYear && (

                <span>
                  {releaseYear}
                </span>

              )}


              {genres.map(
                (genre) => (

                  <span key={genre}>
                    {genre}
                  </span>

                )
              )}

            </div>


            {/* DESCRIPTION */}

            <p className="movie-description">

              {movie.overview ||
                "No description available."}

            </p>


            {/* ==================================================
                USER RATING
            ================================================== */}

            <div className="rating-section">

              <h3>
                Rate this movie
              </h3>


              <div className="rating-stars">

                {[1, 2, 3, 4, 5].map(
                  (star) => (

                    <button
                      key={star}
                      type="button"

                      className={
                        star <=
                        (
                          hoverRating ||
                          userRating
                        )

                          ? "star active"

                          : "star"
                      }

                      onMouseEnter={() =>
                        setHoverRating(
                          star
                        )
                      }

                      onMouseLeave={() =>
                        setHoverRating(
                          0
                        )
                      }

                      onClick={() =>
                        handleRating(
                          star
                        )
                      }

                      disabled={
                        ratingLoading
                      }

                      aria-label={
                        `Rate ${star} out of 5`
                      }

                    >

                      ★

                    </button>

                  )
                )}

              </div>


              <p className="rating-text">

                {ratingLoading

                  ? "Saving rating..."

                  : userRating > 0

                    ? `You rated this movie ${userRating}/5`

                    : "Click a star to rate"

                }

              </p>


              {ratingMessage && (

                <p className="rating-message">

                  {ratingMessage}

                </p>

              )}

            </div>


            {/* ==================================================
                MY LIST
            ================================================== */}

            <div className="movie-actions">

              <button
                className="list-button"
                onClick={handleMyList}
              >

                {isSaved
                  ? "♥ Remove from My List"
                  : "♡ Add to My List"}

              </button>

            </div>


            {/* ==================================================
                SOURCE INFORMATION
            ================================================== */}

            {isTMDBMovie && (

              <div className="cast-section">

                <h3>
                  Movie Information
                </h3>

                <div className="cast-list">

                  <span>
                    TMDB ID: {movie.tmdb_id}
                  </span>

                  <span>
                    Database ID: {movie.movie_id}
                  </span>

                  {movie.vote_count !==
                    undefined && (

                    <span>
                      TMDB Votes:{" "}
                      {movie.vote_count}
                    </span>

                  )}

                </div>

              </div>

            )}


            {/* ==================================================
                RUNTIME
            ================================================== */}

            {movie.runtime && (

              <div className="cast-section">

                <h3>
                  Runtime
                </h3>

                <div className="cast-list">

                  <span>
                    {movie.runtime} minutes
                  </span>

                </div>

              </div>

            )}

          </div>

        </div>

      </section>


      {/* ==================================================
          BACK BUTTON
      ================================================== */}

      <div className="back-section">

        <Link to="/home">
          ← Back to Discover
        </Link>

      </div>


    </div>

  );

}

export default MovieDetails;