import { useState } from "react";
import { useAuth } from "../features/auth/AuthContext";
import "../styles/Login.css";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

function Login() {
  const { login } = useAuth();
const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
   await login(email, password);

setPassword("");
navigate("/dashboard", { replace: true });

    } catch (err) {
      const errorMessages = {
        "auth/invalid-credential":
          "Invalid email or password.",
        "auth/invalid-email":
          "Please enter a valid email address.",
        "auth/too-many-requests":
          "Too many attempts. Please try again later.",
        "auth/network-request-failed":
          "Network error. Please check your internet connection.",
      };

      setError(
        errorMessages[err.code] ||
        "Login failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">

        <h1>Welcome Back</h1>

        <p>Login to your Interview Platform account.</p>

        <form onSubmit={handleSubmit}>

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
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p className="error-message">{error}</p>
          )}

          {success && (
            <p className="success-message">{success}</p>
          )}

          <button
            type="submit"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>
        <p className="register-link">
  Don't have an account?{" "}
  <Link to="/register">Create Account</Link>
</p>

      </div>
    </div>
  );
}

export default Login;