import "./MyList.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function MyList() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ================= LOAD FAVORITES FROM FASTAPI =================

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const userId = localStorage.getItem("user_id");

        if (!userId) {
          setError("Please login first.");
          setLoading(false);
          return;
        }

        const response = await fetch(
          `http://127.0.0.1:8000/favorites/user/${userId}`
        );

        const data = await response.json();

        console.log("Favorites from API:", data);

        if (!response.ok) {
          setError(
            data.detail || "Failed to load your My List."
          );
          return;
        }

        setMovies(data.favorites || []);

      } catch (error) {
        console.error("Error fetching favorites:", error);

        setError(
          "Cannot connect to FastAPI server."
        );

      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, []);


  // ================= REMOVE MOVIE FROM MY LIST =================

  const removeMovie = async (movieId) => {
    try {
      const userId = localStorage.getItem("user_id");

      if (!userId) {
        setError("Please login first.");
        return;
      }

      const response = await fetch(
        `http://127.0.0.1:8000/favorites/${userId}/${movieId}`,
        {
          method: "DELETE"
        }
      );

      const data = await response.json();

      console.log("Remove favorite response:", data);

      if (!response.ok) {
        alert(
          data.detail ||
          "Failed to remove movie from My List."
        );
        return;
      }

      // Remove movie from React state
      setMovies((currentMovies) =>
        currentMovies.filter(
          (movie) =>
            Number(movie.movie_id) !== Number(movieId)
        )
      );

    } catch (error) {
      console.error("Error removing favorite:", error);

      alert(
        "Cannot connect to FastAPI server."
      );
    }
  };


  // ================= LOADING =================

  if (loading) {
    return (
      <div className="my-list-page">
        <nav className="navbar">
          <div className="logo">
            <span>🎬</span> Cine Suggestion
          </div>
          <div className="nav-links">
            <Link to="/home">Discover</Link>
            <Link to="/recommendations">My Recommendations</Link>
            <Link to="/my-list" className="active">My List</Link>
            <Link to="/history">History</Link>
          </div>
          <Link to="/profile" className="profile-circle">A</Link>
        </nav>
        <div className="empty-list">
          <h2>
            Loading My List...
          </h2>
          <p>
            Please wait while your saved movies are loading.
          </p>
        </div>
      </div>
    );
  }


  // ================= ERROR =================

  if (error) {
    return (
      <div className="my-list-page">
        <nav className="navbar">
          <div className="logo">
            <span>🎬</span> Cine Suggestion
          </div>
          <div className="nav-links">
            <Link to="/home">Discover</Link>
            <Link to="/recommendations">My Recommendations</Link>
            <Link to="/my-list" className="active">My List</Link>
            <Link to="/history">History</Link>
          </div>
          <Link to="/profile" className="profile-circle">A</Link>
        </nav>
        <div className="empty-list">
          <div className="empty-icon">
            ♡
          </div>
          <h2>
            {error}
          </h2>
          <Link
            to="/home"
            className="browse-button"
          >
            Discover Movies
          </Link>
        </div>
      </div>
    );
  }


  // ================= PAGE =================

  return (
    <div className="my-list-page">

      {/* ================= NAVBAR ================= */}

      <nav className="navbar">

        <div className="logo">
          <span>🎬</span> Cine Suggestion
        </div>

        <div className="nav-links">

          <Link to="/home">
            Discover
          </Link>

          <Link to="/recommendations">
            My Recommendations
          </Link>

          <Link
            to="/my-list"
            className="active"
          >
            My List
          </Link>

          <Link to="/history">
            History
          </Link>

        </div>

        <Link to="/profile" className="profile-circle">
          A
        </Link>

      </nav>


      {/* ================= HEADER ================= */}

      <div className="my-list-header">

        <p>
          YOUR COLLECTION
        </p>

        <h1>
          My List
        </h1>

        <span>
          Movies you've saved to watch later.
        </span>

      </div>


      {/* ================= SAVED MOVIES ================= */}

      {movies.length > 0 ? (

        <div className="my-list-grid">

          {movies.map((movie) => (

            <div
              className="my-list-card"
              key={movie.movie_id}
            >

              <Link
                to={`/movie-details/${movie.movie_id}`}
                className="my-list-movie-link"
              >

                <div className="my-list-poster">

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


                <h3>
                  {movie.title}
                </h3>


                <p>
                  {movie.genres
                    ? movie.genres.replace(/\|/g, " / ")
                    : "No genres available"}
                </p>

              </Link>


              {/* ================= REMOVE BUTTON ================= */}

              <button
                className="remove-button"
                onClick={() =>
                  removeMovie(movie.movie_id)
                }
                title="Remove from My List"
              >
                ♥
              </button>

            </div>

          ))}

        </div>

      ) : (

        /* ================= EMPTY LIST ================= */

        <div className="empty-list">

          <div className="empty-icon">
            ♡
          </div>

          <h2>
            Your List is Empty
          </h2>

          <p>
            Save movies you want to watch later.
          </p>

          <Link
            to="/home"
            className="browse-button"
          >
            Discover Movies
          </Link>

        </div>

      )}

    </div>
  );
}

export default MyList;
