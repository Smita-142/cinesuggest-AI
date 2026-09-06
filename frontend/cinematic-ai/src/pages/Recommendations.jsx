import "./Recommendations.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [historyCount, setHistoryCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError("");

        const userId = localStorage.getItem("user_id");

        if (!userId) {
          setError("Please login first.");
          setLoading(false);
          return;
        }

        const response = await fetch(
          `http://127.0.0.1:8000/recommendations/${userId}?n=10`
        );

        const data = await response.json();

        console.log("Recommendation API:", data);

        if (!response.ok) {
          setError(
            typeof data.detail === "string"
              ? data.detail
              : "Failed to load recommendations"
          );
          setLoading(false);
          return;
        }

        setRecommendations(data.recommendations || []);

        // Keep this only for the message on the page.
        const history =
          JSON.parse(localStorage.getItem("watchHistory")) || [];

        setHistoryCount(history.length);
      } catch (error) {
        console.error("Recommendation error:", error);
        setError(
          "Cannot connect to recommendation server."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  return (
    <div className="recommendations-page">

      <nav className="navbar">

        <div className="logo">
          <span>🎬</span> Cinematic AI
        </div>

        <div className="nav-links">

          <Link to="/home">
            Discover
          </Link>

          <Link
            to="/recommendations"
            className="active"
          >
            My Recommendations
          </Link>

          <Link to="/my-list">
            My List
          </Link>

          <Link to="/history">
            History
          </Link>

        </div>

        <div className="profile-circle">
          A
        </div>

      </nav>


      <div className="recommendations-header">

        <p>AI POWERED</p>

        <h1>
          My Recommendations
        </h1>

        <span>
          Movies selected by AI based on your
          ratings and preferences.
        </span>

      </div>


      <div className="ai-message">

        <div className="ai-icon">
          ✦
        </div>

        <div>

          <h3>
            Your AI Movie Guide
          </h3>

          {loading ? (

            <p>
              Finding movies for you...
            </p>

          ) : historyCount > 0 ? (

            <p>
              We've analyzed your movie activity
              and found recommendations specially
              selected for you.
            </p>

          ) : (

            <p>
              Rate some movies to help our AI
              understand your taste.
            </p>

          )}

        </div>

      </div>


      {loading && (

        <div className="no-recommendations">

          <div className="empty-ai-icon">
            ✦
          </div>

          <h2>
            Finding Your Movies...
          </h2>

          <p>
            Our recommendation engine is analyzing
            your preferences.
          </p>

        </div>

      )}


      {!loading && error && (

        <div className="no-recommendations">

          <div className="empty-ai-icon">
            ⚠
          </div>

          <h2>
            Unable to Load Recommendations
          </h2>

          <p>
            {error}
          </p>

          <Link
            to="/home"
            className="discover-button"
          >
            Go to Discover
          </Link>

        </div>

      )}


      {!loading &&
        !error &&
        recommendations.length > 0 && (

          <section className="recommendation-section">

            <div className="section-heading">

              <div>

                <p>
                  PERSONALIZED FOR YOU
                </p>

                <h2>
                  Recommended Movies
                </h2>

              </div>

            </div>


            <div className="recommendation-grid">

              {recommendations.map((movie) => (

                <Link
                  key={movie.movie_id}
                  to={`/movie-details/${movie.movie_id}`}
                  className="recommendation-card"
                >

                  <div className="recommendation-poster">

                    <img
                      src={
                        movie.poster_url ||
                        "/images/default-movie.jpg"
                      }
                      alt={movie.title}
                    />

                    <span>
                      ★{" "}
                      {movie.match_percentage != null
                        ? `${movie.match_percentage}%`
                        : movie.hybrid_score?.toFixed(1)}
                    </span>

                  </div>


                  <h3>
                    {movie.title}
                  </h3>


                  <p>
                    {movie.release_year || "N/A"}
                    {" • "}
                    {movie.genres || "Unknown"}
                  </p>


                  {movie.match_percentage != null && (

                    <div className="why-recommended">

                      ✦ Recommended for you{" "}

                      <strong>
                        {movie.match_percentage}%
                        match
                      </strong>

                    </div>

                  )}

                </Link>

              ))}

            </div>

          </section>

        )}


      {!loading &&
        !error &&
        recommendations.length === 0 && (

          <div className="no-recommendations">

            <div className="empty-ai-icon">
              ✦
            </div>

            <h2>
              We Need More Data
            </h2>

            <p>
              Rate a few movies so our AI can
              understand your preferences and
              create personalized recommendations.
            </p>

            <Link
              to="/home"
              className="discover-button"
            >
              Discover Movies
            </Link>

          </div>

        )}

    </div>
  );
}

export default Recommendations;