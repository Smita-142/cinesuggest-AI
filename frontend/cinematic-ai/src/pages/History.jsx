import "./History.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function History() {

  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // ============================================================
  // LOAD WATCH HISTORY FROM FASTAPI
  // ============================================================

  useEffect(() => {

    const fetchHistory = async () => {

      try {

        const userId = localStorage.getItem("user_id");

        // User not logged in
        if (!userId) {

          setError("Please login first.");
          setLoading(false);

          return;
        }


        const response = await fetch(
          `http://127.0.0.1:8000/watch-history/user/${userId}`
        );


        const data = await response.json();


        console.log(
          "Watch History from API:",
          data
        );


        if (!response.ok) {

          setError(
            data.detail ||
            "Failed to load watch history."
          );

          return;
        }


        // Get watch_history array
        setMovies(
          data.watch_history || []
        );


      } catch (error) {

        console.error(
          "Error fetching watch history:",
          error
        );


        setError(
          "Cannot connect to FastAPI server."
        );


      } finally {

        setLoading(false);

      }

    };


    fetchHistory();

  }, []);


  // ============================================================
  // REMOVE ONE MOVIE FROM HISTORY
  // ============================================================

  const removeMovie = async (movieId) => {

    try {

      const userId =
        localStorage.getItem("user_id");


      if (!userId) {

        alert("Please login first.");

        return;
      }


      const response = await fetch(

        `http://127.0.0.1:8000/watch-history/${userId}/${movieId}`,

        {
          method: "DELETE"
        }

      );


      const data = await response.json();


      console.log(
        "Remove history response:",
        data
      );


      if (!response.ok) {

        alert(
          data.detail ||
          "Failed to remove movie from history."
        );

        return;
      }


      // Remove movie from screen
      setMovies((currentMovies) =>

        currentMovies.filter(

          (movie) =>
            Number(movie.movie_id) !==
            Number(movieId)

        )

      );


    } catch (error) {

      console.error(
        "Error removing history:",
        error
      );


      alert(
        "Cannot connect to FastAPI server."
      );

    }

  };


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {

    return (

      <div className="history-page">

        <div className="empty-history">

          <div className="empty-history-icon">
            ◷
          </div>

          <h2>
            Loading History...
          </h2>

          <p>
            Please wait while your watch history is loading.
          </p>

        </div>

      </div>

    );

  }


  // ============================================================
  // ERROR
  // ============================================================

  if (error) {

    return (

      <div className="history-page">

        <div className="empty-history">

          <div className="empty-history-icon">
            ◷
          </div>

          <h2>
            {error}
          </h2>

          <Link
            to="/home"
            className="browse-history-button"
          >
            Discover Movies
          </Link>

        </div>

      </div>

    );

  }


  // ============================================================
  // PAGE
  // ============================================================

  return (

    <div className="history-page">


      {/* ========================================================
          NAVBAR
      ======================================================== */}

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


          <Link
            to="/history"
            className="active"
          >
            History
          </Link>


        </div>


        <div className="profile-circle">
          A
        </div>


      </nav>



      {/* ========================================================
          HEADER
      ======================================================== */}

      <div className="history-header">


        <div>

          <p>
            YOUR ACTIVITY
          </p>


          <h1>
            Watch History
          </h1>


          <span>
            Movies you've recently viewed.
          </span>

        </div>


      </div>



      {/* ========================================================
          MOVIES
      ======================================================== */}

      {movies.length > 0 ? (

        <div className="history-grid">


          {movies.map((movie) => (


            <div
              className="history-card"
              key={movie.id}
            >


              <Link
                to={`/movie-details/${movie.movie_id}`}
                className="history-movie-link"
              >


                {/* POSTER */}

                <div className="history-poster">


                  <img
                    src={
                      movie.poster_url ||
                      "/images/default-movie.jpg"
                    }
                    alt={movie.title}
                  />


                </div>



                {/* TITLE */}

                <h3>
                  {movie.title}
                </h3>



                {/* GENRES */}

                <p>

                  {movie.genres
                    ? movie.genres.replace(
                        /\|/g,
                        " / "
                      )
                    : "No genres available"}

                </p>


              </Link>



              {/* ==================================================
                  REMOVE BUTTON
              ================================================== */}

              <button
                className="remove-history-button"
                onClick={() =>
                  removeMovie(movie.movie_id)
                }
                title="Remove from History"
              >

                ×

              </button>


            </div>

          ))}


        </div>

      ) : (


        /* ========================================================
           EMPTY HISTORY
        ======================================================== */

        <div className="empty-history">


          <div className="empty-history-icon">
            ◷
          </div>


          <h2>
            No Watch History
          </h2>


          <p>
            Movies you view will appear here.
          </p>


          <Link
            to="/home"
            className="browse-history-button"
          >
            Discover Movies
          </Link>


        </div>

      )}


    </div>

  );

}

export default History;
