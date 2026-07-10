import { useState } from "react";
import axios from "axios";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const validate = () => {
    if (!email.trim() || !password.trim()) {
      setError("Please enter email and password.");
      return false;
    }
    setError("");
    return true;
  };

  const loginUser = async () => {
    if (!validate()) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.post("https://aktubot-production.up.railway.app/login", {
        email,
        password,
      });

      localStorage.setItem("user", JSON.stringify(response.data.user));
      setSuccess("Login successful — redirecting...");
      setTimeout(() => window.location.reload(), 700);
    } catch (err) {
      const message = err?.response?.data?.detail || err?.response?.data?.message || "Login failed. Please check credentials.";
      setError(message);
      setSuccess("");
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") loginUser();
  };

  return (
    <div>
      <h2>Login</h2>

      <div className="form">
        <div className="form-field">
          <input
            className="form-input"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={onKeyDown}
          />
        </div>

        <div className="form-field">
          <input
            className="form-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={onKeyDown}
          />
        </div>

        <div className="form-actions">
          <button onClick={loginUser} disabled={loading}>
            {loading ? <div className="spinner" /> : "Login"}
          </button>

          <span className="small-muted">Forgot password? Contact admin.</span>
        </div>

        {error && <div className="error-text">{error}</div>}
        {success && <div className="success-text">{success}</div>}
      </div>
    </div>
  );
}

export default Login;