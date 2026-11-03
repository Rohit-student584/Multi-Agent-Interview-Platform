
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import api from "../api/axios";

function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    if (name.trim().length < 2) {
      setError("Name must contain at least 2 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      // Create Firebase account
      await register(email.trim(), password);

      // Save user profile in MongoDB through API Gateway
      await api.put("/api/users/me", {
        name: name.trim(),
        target_role: null,
        skills: [],
      });

      // Registration and profile creation successful
      navigate("/dashboard", { replace: true });

    } catch (err) {
      const errorMessages = {
        "auth/email-already-in-use":
          "This email is already registered.",
        "auth/invalid-email":
          "Please enter a valid email address.",
        "auth/weak-password":
          "Please choose a stronger password.",
        "auth/network-request-failed":
          "Network error. Please check your internet connection.",
      };

      setError(
        errorMessages[err.code] ||
        err.response?.data?.detail ||
        "Registration failed. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">

        <h1>Create Account</h1>

        <p>Join the Multi-Agent Interview Platform.</p>

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="name">Full Name</label>

            <input
              id="name"
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>

            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>

            <input
              id="password"
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={6}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">
              Confirm Password
            </label>

            <input
              id="confirmPassword"
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p className="error-message">{error}</p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Creating Account..." : "Register"}
          </button>

        </form>

        <p>
          Already have an account?{" "}
          <Link to="/login">Login</Link>
        </p>

      </div>
    </div>
  );
}

export default Register;
