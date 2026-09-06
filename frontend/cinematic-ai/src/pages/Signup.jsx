import "./Signup.css";
import { useNavigate, Link } from "react-router-dom";
import { useState } from "react";

function Signup() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");

    // Check passwords
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: username,
            email: email,
            password: password,
          }),
        }
      );

      const data = await response.json();

      // Registration failed
      if (!response.ok) {
           console.log("FastAPI error:", data);
           setError(JSON.stringify(data.detail));
    
        return;
      }

      // Registration successful
      alert("Account created successfully!");
      // Go to Login page
      navigate("/");
    } catch (error) {
      console.error("Signup error:", error);
      setError(
        "Cannot connect to server. Is FastAPI running?"
      );
    }
  };

  return (
    <div className="signup-page">

      {/* Left Side - Movie Visual */}
      <div className="signup-visual">

        <div className="signup-visual-overlay">
          <h1>Cinematic AI</h1>

          <p>
            Your next favorite movie
            is waiting for you.
          </p>
        </div>

      </div>


      {/* Right Side - Signup Form */}
      <div className="signup-form-section">

        <div className="signup-container">

          <h2>Create Account</h2>

          <p className="signup-subtitle">
            Join Cinematic AI and discover movies made for you.
          </p>


          <form onSubmit={handleSignup}>
            <input
                type="text"
                placeholder="Enter your name"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />


            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />


            <input
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />


            <input
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />


            <button
              type="submit"
              className="signup-button"
            >
              Create Account
            </button>

          </form>


          <p className="login-text">

            Already have an account?

            <Link to="/">
              {" "}Sign In
            </Link>

          </p>

        </div>

      </div>

    </div>
  );
}

export default Signup;