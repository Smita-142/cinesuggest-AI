import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Recommendations from "./pages/Recommendations";
import MyList from "./pages/MyList";
import History from "./pages/History";
import MovieDetails from "./pages/MovieDetails";
import Profile from "./pages/Profile";
import ChangePassword from "./pages/ChangePassword";
import ForgotPassword from "./pages/ForgotPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ================= AUTH ================= */}

        <Route path="/" element={<Login />} />

        <Route path="/login" element={<Login />} />

        <Route path="/signup" element={<Signup />} />

        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        <Route
          path="/change-password"
          element={<ChangePassword />}
        />


        {/* ================= MAIN PAGES ================= */}

        <Route
          path="/home"
          element={<Home />}
        />

        <Route
          path="/search"
          element={<Search />}
        />

        <Route
          path="/profile"
          element={<Profile />}
        />

        <Route
          path="/recommendations"
          element={<Recommendations />}
        />

        <Route
          path="/my-list"
          element={<MyList />}
        />

        <Route
          path="/history"
          element={<History />}
        />


        {/* ================= MOVIE DETAILS ================= */}

        {/* TMDB movie details */}
        <Route
          path="/movie-details/tmdb/:tmdbId"
          element={<MovieDetails />}
        />

        {/* MySQL / MovieLens movie details */}
        <Route
          path="/movie-details/:id"
          element={<MovieDetails />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;