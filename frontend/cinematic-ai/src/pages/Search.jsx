import "./Search.css";

import { useEffect, useState } from "react";

import { Link } from "react-router-dom";
import { API_BASE_URL } from "../config/api";


function Search() {

  const [query, setQuery] = useState("");

  const [movies, setMovies] = useState([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [source, setSource] = useState("");


  // ==================================================
  // GET MOVIES FROM FASTAPI
  // ==================================================

  useEffect(() => {

    const searchMovies = async () => {

      try {

        setLoading(true);

        setError("");

        setSource("");


        // ----------------------------------------------
        // DEFAULT: GET MOVIES FROM MYSQL
        // ----------------------------------------------

        let url =
          `${API_BASE_URL}/movies/`;


        // ----------------------------------------------
        // SEARCH: MYSQL FIRST → TMDB IF NOT FOUND
        // ----------------------------------------------

        if (query.trim() !== "") {

          url =
            `${API_BASE_URL}/movies/search?title=${encodeURIComponent(
              query.trim()
            )}`;

        }


        // ----------------------------------------------
        // CALL FASTAPI
        // ----------------------------------------------

        const response = await fetch(url);

        const data = await response.json();


        console.log("Movies from API:", data);


        // ----------------------------------------------
        // ERROR
        // ----------------------------------------------

        if (!response.ok) {

          setError(
            data.detail || "Failed to fetch movies"
          );

          setMovies([]);

          return;

        }


        // ----------------------------------------------
        // SEARCH RESPONSE
        //
        // New API returns:
        //
        // {
        //   source: "database" / "tmdb",
        //   results: [...]
        // }
        // ----------------------------------------------

        if (query.trim() !== "") {

          setMovies(data.results || []);

          setSource(data.source || "");

        }

        // ----------------------------------------------
        // ALL MOVIES RESPONSE
        //
        // /movies/ returns an array directly
        // ----------------------------------------------

        else {

          setMovies(data || []);

          setSource("database");

        }

      }

      catch (error) {

        console.error(
          "Search error:",
          error
        );

        setError(
          "Cannot connect to FastAPI server."
        );

        setMovies([]);

      }

      finally {

        setLoading(false);

      }

    };


    searchMovies();

  }, [query]);


  // ==================================================
  // RENDER
  // ==================================================

  return (

    <div className="search-page">


      {/* ==================================================
          NAVBAR
      ================================================== */}

      <nav className="navbar">

        <div className="logo">

          <span>🎬</span>

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
          SEARCH HEADER
      ================================================== */}

      <section className="search-header">

        <p>
          SEARCH MOVIES
        </p>


        <h1>
          Find Your Next Movie
        </h1>


        <span>
          Search for movies by title, genre or your
          favorite characters.
        </span>


        <div className="search-large">

          <span>
            🔍
          </span>


          <input
            type="text"
            placeholder="Search for movies..."
            value={query}
            onChange={(e) =>
              setQuery(e.target.value)
            }
          />

        </div>

      </section>


      {/* ==================================================
          SEARCH RESULTS
      ================================================== */}

      <section className="search-results">


        <div className="results-heading">

          <h2>

            {query.trim() === ""

              ? "All Movies"

              : `Search Results for "${query}"`

            }

          </h2>


          <span>

            {loading

              ? "Searching..."

              : `${movies.length} ${
                  movies.length === 1
                    ? "movie"
                    : "movies"
                } found`

            }

          </span>

        </div>


        {/* ==================================================
            SOURCE INFORMATION
        ================================================== */}

        {!loading &&
          !error &&
          query.trim() !== "" &&
          movies.length > 0 &&
          source && (

            <p
              style={{
                marginBottom: "20px",
                color: "#aaa"
              }}
            >

              {source === "database"

                ? "🎬 Results from our movie database"

                : source === "tmdb"

                ? "🌐 Movie found using TMDB"

                : ""

              }

            </p>

          )}


        {/* ==================================================
            ERROR
        ================================================== */}

        {error && (

          <div className="no-results">

            <div>
              ⚠️
            </div>


            <h2>
              Unable to Load Movies
            </h2>


            <p>
              {error}
            </p>

          </div>

        )}


        {/* ==================================================
            LOADING
        ================================================== */}

        {!error &&
          loading && (

            <div className="no-results">

              <div>
                🔍
              </div>


              <h2>
                Searching...
              </h2>


              <p>
                Searching our database and TMDB.
              </p>

            </div>

          )}


        {/* ==================================================
            MOVIES
        ================================================== */}

        {!loading &&
          !error &&
          movies.length > 0 && (

            <div className="search-grid">

              {movies.map((movie, index) => {


                // ------------------------------------------
                // Determine whether movie is from TMDB
                // ------------------------------------------

                const isTMDBMovie =
                  source === "tmdb" ||
                  movie.source === "tmdb";


                // ------------------------------------------
                // Create unique key
                // ------------------------------------------

                const movieKey =
                  movie.movie_id ||
                  movie.tmdb_id ||
                  index;


                // ------------------------------------------
                // Movie details URL
                // ------------------------------------------

                const detailsUrl =
                  isTMDBMovie

                    ? `/movie-details/tmdb/${movie.tmdb_id}`

                    : `/movie-details/${movie.movie_id}`;


                return (

                  <Link
                    key={movieKey}
                    to={detailsUrl}
                    className="search-card"
                  >


                    {/* ======================================
                        POSTER
                    ====================================== */}

                    <div className="search-poster">

                      <img
                        src={
                          movie.poster_url ||
                          "/images/default-movie.jpg"
                        }

                        alt={
                          movie.title ||
                          "Movie"
                        }

                        onError={(e) => {
                          e.currentTarget.onerror = null;
                          e.currentTarget.src =
                            "/images/default-movie.jpg";
                        }}

                      />


                      {/* RATING */}

                      {movie.rating != null && (

                        <span className="search-rating">

                          ★{" "}
                          {Number(movie.rating).toFixed(1)}

                        </span>

                      )}

                    </div>


                    {/* ======================================
                        TITLE
                    ====================================== */}

                    <h3>

                      {movie.title ||
                        movie.original_title ||
                        "Unknown Movie"}

                    </h3>


                    {/* ======================================
                        YEAR + GENRE
                    ====================================== */}

                    <p>

                      {movie.release_year

                        ? movie.release_year

                        : movie.release_date

                        ? movie.release_date.substring(
                            0,
                            4
                          )

                        : "N/A"

                      }


                      {" • "}


                      {movie.genres

                        ? movie.genres.replace(
                            /\|/g,
                            " / "
                          )

                        : "Unknown"

                      }

                    </p>


                    {/* ======================================
                        TMDB LABEL
                    ====================================== */}

                    {isTMDBMovie && (

                      <small
                        style={{
                          color: "#aaa",
                          display: "block",
                          marginTop: "5px"
                        }}
                      >
                        TMDB
                      </small>

                    )}

                  </Link>

                );

              })}

            </div>

          )}


        {/* ==================================================
            NO RESULTS
        ================================================== */}

        {!loading &&
          !error &&
          movies.length === 0 && (

            <div className="no-results">

              <div>
                🔍
              </div>


              <h2>
                No Movies Found
              </h2>


              <p>
                Try searching with another movie title.
              </p>

            </div>

          )}

      </section>

    </div>

  );

}


export default Search;
