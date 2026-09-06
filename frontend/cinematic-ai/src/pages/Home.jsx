import "./Home.css";
import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config/api";

function Home() {

  const navigate = useNavigate();

  // ================= MOVIES STATE =================

  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // ================= GET TOP RATED MOVIES =================

  useEffect(() => {

    const fetchTopRatedMovies = async () => {

      try {

        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/movies/top-rated`
        );

        const data = await response.json();

        console.log("Top Rated Movies:", data);

        if (!response.ok) {

          setError(
            data.detail ||
            "Failed to load movies."
          );

          return;
        }

        setMovies(data);

      } catch (error) {

        console.error(
          "Error fetching top rated movies:",
          error
        );

        setError(
          "Cannot connect to FastAPI server."
        );

      } finally {

        setLoading(false);

      }

    };

    fetchTopRatedMovies();

  }, []);


  // ================= RETURN =================

  return (

    <div className="home-page">


      {/* ================= NAVBAR ================= */}

      <nav className="navbar">

        <div className="logo">
          <span>🎬</span> Cine Suggestion
        </div>


        <div className="nav-links">

          <Link
            className="active"
            to="/home"
          >
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


      <div className="profile">
        <Link to="/profile" className="profile-circle">
          A
        </Link>
      </div>

        </nav>



      {/* ================= WELCOME SECTION ================= */}

      <section className="welcome-section">

        <div className="welcome-content">


          <p className="small-title">
            YOUR PERSONAL AI MOVIE GUIDE
          </p>


          <h1>
            Welcome to <span>Cine Suggestion</span>
          </h1>


          <p className="welcome-text">
            Discover movies you'll love, personalized just for you.
          </p>



          {/* ================= SEARCH ================= */}

          <div className="search-box">

            <span>🔍</span>


            <input
              type="text"
              placeholder="Search for movies, actors, genres..."
              onKeyDown={(event) => {

                if (event.key === "Enter") {
                  navigate("/search");
                }

              }}
            />


            <button
              onClick={() => navigate("/search")}
            >
              Search
            </button>

          </div>

        </div>

      </section>



      {/* ================= TOP RATED MOVIES ================= */}

      <section className="movie-section">


        <div className="section-heading">


          <div>

            <p className="section-label">
              TOP RATED
            </p>


            <h2>
              Best Rated Movies
            </h2>

          </div>


          <button
            className="view-all"
            onClick={() => navigate("/search")}
          >
            View All →
          </button>

        </div>



        {/* ================= MOVIE GRID ================= */}

        {loading ? (

          <div className="loading-message">

            <p>
              Loading top rated movies...
            </p>

          </div>

        ) : error ? (

          <div className="loading-message">

            <p>
              {error}
            </p>

          </div>

        ) : movies.length === 0 ? (

          <div className="loading-message">

            <p>
              No rated movies found.
            </p>

          </div>

        ) : (

          <div className="movie-grid">

            {movies.map((movie) => (

              <Link
                key={movie.movie_id}
                to={`/movie-details/${movie.movie_id}`}
                className="movie-card"
              >


                {/* ================= POSTER ================= */}

                <div className="movie-poster">

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


                  {/* ================= RATING ================= */}

                  <span className="rating">

                    ★{" "}

                    {movie.rating !== null &&
                    movie.rating !== undefined
                      ? Number(movie.rating).toFixed(1)
                      : "N/A"}

                  </span>

                </div>



                {/* ================= TITLE ================= */}

                <h3>
                  {movie.title}
                </h3>



                {/* ================= INFO ================= */}

                <p>

                  {movie.release_year
                    ? movie.release_year
                    : ""}

                  {movie.release_year &&
                  movie.genres
                    ? " • "
                    : ""}

                  {movie.genres
                    ? movie.genres.replace(
                        /\|/g,
                        " / "
                      )
                    : ""}

                </p>


              </Link>

            ))}

          </div>

        )}

      </section>



      {/* ================= AI RECOMMENDATIONS ================= */}

      <section className="movie-section">


        <div className="section-heading">


          <div>

            <p className="section-label">
              AI PICKS FOR YOU
            </p>


            <h2>
              Recommended For You
            </h2>

          </div>

        </div>



        <div className="recommendation-box">


          <div className="ai-icon">
            ✦
          </div>


          <div>

            <h3>
              AI-Powered Recommendations
            </h3>


            <p>
              Our AI learns your taste and finds movies
              that match your interests.
            </p>

          </div>



          <Link
            to="/recommendations"
            className="recommendation-button"
          >
            Explore Recommendations
          </Link>


        </div>

      </section>


    </div>

  );

}

export default Home;
