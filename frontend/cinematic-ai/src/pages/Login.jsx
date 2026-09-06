import "./Login.css";
import { useNavigate, Link } from "react-router-dom";
import { useState } from "react";
import { API_BASE_URL } from "../config/api";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/auth/login`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },

          body: new URLSearchParams({
            email: email,
            password: password,
          }),
        }
      );

      const data = await response.json();

      // Login failed
      if (!response.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : "Login failed"
        );

        return;
      }

      // Login successful
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("username", data.username);
      localStorage.setItem("email", data.email);

      // Go to Home
      navigate("/home");

    } catch (error) {
      console.error("Login error:", error);

      setError(
        "Cannot connect to server. Is FastAPI running?"
      );
    }
  };

  return (
    <div className="login-page">

      {/* LEFT SIDE */}
      <div className="login-visual">

        <div className="visual-overlay">

          <h1>Cine Suggestion</h1>

          <p>
            Discover movies you'll love,
            powered by AI.
          </p>

        </div>

      </div>


      {/* RIGHT SIDE */}
      <div className="login-form-section">

        <div className="login-container">

          <h2>Welcome Back</h2>

          <p className="login-subtitle">
            Sign in to continue your cinematic journey
          </p>


          <form onSubmit={handleLogin}>

            {/* EMAIL */}

            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />


            {/* PASSWORD */}

            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              name="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />


            {/* ERROR */}

            {error && (
              <p
                style={{
                  color: "red",
                  marginBottom: "15px",
                }}
              >
                {error}
              </p>
            )}


            {/* OPTIONS */}

            <div className="login-options">

              <label className="remember">

                <input
                  type="checkbox"
                  id="remember"
                  name="remember"
                />

                Remember me

              </label>

              {/* FORGOT PASSWORD */}
              <Link to="/forgot-password">
                Forgot Password?
              </Link>

            </div>


            {/* LOGIN BUTTON */}

            <button
              type="submit"
              className="login-button"
            >
              Sign In
            </button>

          </form>


          {/* SIGNUP */}

          <p className="signup-text">

            Don't have an account?

            <Link to="/signup">
              {" "}Create Account
            </Link>

          </p>

        </div>

      </div>

    </div>
  );
}

export default Login;

