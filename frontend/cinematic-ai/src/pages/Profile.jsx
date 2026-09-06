import "./Profile.css";
import { Link, useNavigate } from "react-router-dom";

import {
  getCurrentUser,
  logoutUser,
} from "../auth/auth";

function Profile() {

  const navigate = useNavigate();

  const user = getCurrentUser();

  const savedMovies =
    JSON.parse(localStorage.getItem("myList")) || [];

  const watchHistory =
    JSON.parse(localStorage.getItem("watchHistory")) || [];


  const handleLogout = () => {

    logoutUser();

    navigate("/login", { replace: true });
  };


  return (
    <div className="profile-page">

      {/* ================= NAVBAR ================= */}

      <nav className="navbar">

        <div className="logo">
          <span>🎬</span> Cinematic AI
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
          {user?.name?.charAt(0).toUpperCase() || "A"}
        </Link>

      </nav>


      {/* ================= PROFILE ================= */}

      <main className="profile-container">

        <section className="profile-header">

          <div className="profile-avatar">
            {user?.name?.charAt(0).toUpperCase() || "A"}
          </div>


          <div className="profile-info">

            <div className="profile-name-row">

              <h1>
                {user?.name || "CineMatch User"}
              </h1>

              <span className="member-badge">
                CineMatch Member
              </span>

            </div>

            <p>
              {user?.email || "user@gmail.com"}
            </p>

          </div>


          <button className="edit-profile">
            Edit Profile
          </button>

        </section>


        {/* ================= STATS ================= */}

        <section className="profile-stats">

          <div className="stat-card">

            <span>
              Movies Rated
            </span>

            <strong>
              0
            </strong>

          </div>


          <div className="stat-card">

            <span>
              Movies Watched
            </span>

            <strong>
              {watchHistory.length}
            </strong>

          </div>


          <div className="stat-card">

            <span>
              Movies Saved
            </span>

            <strong>
              {savedMovies.length}
            </strong>

          </div>

        </section>


        {/* ================= GENRES ================= */}

        <section className="genres-section">

          <h2>
            Favorite Genres
          </h2>

          <div className="genre-list">

            <span>Action</span>
            <span>Drama</span>
            <span>Comedy</span>
            <span>Sci-Fi</span>
            <span>Thriller</span>

          </div>

        </section>


        {/* ================= ACCOUNT SETTINGS ================= */}

        <section className="account-section">

          <h2>
            Account Settings
          </h2>


          <div className="settings-box">

            <div className="setting-item">

              <div>
                <h3>Account Settings</h3>
                <p>
                  Manage your profile and general system configurations
                </p>
              </div>

              <span>›</span>

            </div>


            <div className="setting-item">

              <div>
                <h3>Change Password</h3>
                <p>
                  Update your account password
                </p>
              </div>

              <span>›</span>

            </div>


            <button
              className="logout-item"
              onClick={handleLogout}
            >

              <div>

                <h3>
                  Logout
                </h3>

                <p>
                  Safely sign out from Cinematic AI
                </p>

              </div>

              <span>
                ⇥
              </span>

            </button>

          </div>

        </section>

      </main>

    </div>
  );
}

export default Profile;