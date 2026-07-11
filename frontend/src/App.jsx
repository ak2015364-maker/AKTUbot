import Login from "./Login";
import Signup from "./Signup";
import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const getStoredUser = () => {
  try {
    const rawUser = localStorage.getItem("user");

    if (!rawUser || rawUser === "undefined") {
      localStorage.removeItem("user");
      return null;
    }

    const parsedUser = JSON.parse(rawUser);

    if (!parsedUser || typeof parsedUser !== "object" || !parsedUser.email) {
      localStorage.removeItem("user");
      return null;
    }

    return parsedUser;
  } catch {
    localStorage.removeItem("user");
    return null;
  }
};

function App() {
  const [user, setUser] = useState(getStoredUser());

  const [showSignup, setShowSignup] = useState(false);

  const [showSidebar, setShowSidebar] = useState(false);
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("theme") === "dark"
  );
  const [history, setHistory] = useState([]);
  const [usernameDraft, setUsernameDraft] = useState(user?.username || "");
  const [usernameLoading, setUsernameLoading] = useState(false);
  const [usernameError, setUsernameError] = useState("");
  const [usernameMessage, setUsernameMessage] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState("DBMS");

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);

    try {
      const response = await axios.post("https://aktubot-production.up.railway.app/ask-rag", {
        subject: selectedSubject,
        question: question,
        user_id: user?.id,
      });

      setAnswer(response.data.answer);
      setSources(response.data.sources || []);
    } catch (error) {
      console.error(error);
      setAnswer("Something went wrong.");
    }

    setLoading(false);
  };

  useEffect(() => {
    setUsernameDraft(user?.username || "");
  }, [user?.id, user?.username]);

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem("theme", next ? "dark" : "light");
    if (next) document.body.classList.add("dark");
    else document.body.classList.remove("dark");
  };

  const updateUsername = async (e) => {
    e.preventDefault();

    if (!user?.id) return;

    const nextUsername = usernameDraft.trim();

    if (!nextUsername) {
      setUsernameError("Username cannot be empty.");
      setUsernameMessage("");
      return;
    }

    setUsernameLoading(true);
    setUsernameError("");
    setUsernameMessage("");

    try {
      const response = await axios.put(`https://aktubot-production.up.railway.app/users/${user.id}/username`, {
        username: nextUsername,
      });

      const updatedUser = {
        ...user,
        username: response.data?.user?.username || nextUsername,
      };

      localStorage.setItem("user", JSON.stringify(updatedUser));
      setUser(updatedUser);
      setUsernameMessage("Username updated successfully.");
    } catch (err) {
      const message = err?.response?.data?.detail || "Unable to update username.";
      setUsernameError(message);
    } finally {
      setUsernameLoading(false);
    }
  };

  const fetchHistory = async () => {
    if (!user) return;
    try {
      const res = await axios.get(`https://aktubot-production.up.railway.app/history/${user.id}`);
      setHistory(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const openSidebar = () => {
    setShowSidebar(true);
    fetchHistory();
  };

  const closeSidebar = () => {
    setShowSidebar(false);
  };

  const logout = () => {
    localStorage.removeItem("user");
    setUser(null);
    setShowSidebar(false);
    setQuestion("");
    setAnswer("");
    setSources([]);
    setHistory([]);
    setUsernameDraft("");
    setUsernameError("");
    setUsernameMessage("");
    window.location.href = window.location.pathname;
  };

  if (!user) {
    return (
      <div className="container">
        <div className="card">
          <h1 className="brand">AKTUbot</h1>

          {!showSignup ? (
            <>
              <Login />

              <div style={{ marginTop: 12 }}>
                <button
                  className="link-button"
                  onClick={() => setShowSignup(true)}
                >
                  New User?
                </button>
              </div>
            </>
          ) : (
            <>
              <Signup />

              <div style={{ marginTop: 12 }}>
                <button
                  className="link-button"
                  onClick={() => setShowSignup(false)}
                >
                  Back to Login
                </button>
              </div>
            </>
          )}

        </div>
      </div>
    );
  }

  return (
    <div className="container">

      <button
        className="hamburger"
        onClick={openSidebar}
        aria-label="Open menu"
      >
        ☰
      </button>

      <div className={"sidebar " + (showSidebar ? "open" : "") }>
        <div className="sidebar-header">
          <strong>{user.username}</strong>
          <button className="close-x" onClick={closeSidebar}>×</button>
        </div>

        <div className="sidebar-section">
          <div className="small-muted">Settings</div>
          <div className="settings-sub">
            <label>
              <input
                type="checkbox"
                checked={darkMode}
                onChange={toggleTheme}
              />
              {' '}Dark mode
            </label>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="small-muted">Change username</div>
          <form className="username-update-form" onSubmit={updateUsername}>
            <input
              className="username-update-input"
              value={usernameDraft}
              onChange={(e) => setUsernameDraft(e.target.value)}
              placeholder="New username"
            />
            <button className="username-update-button" type="submit" disabled={usernameLoading}>
              {usernameLoading ? "Saving..." : "Save"}
            </button>
          </form>
          {usernameError && <div className="error-text">{usernameError}</div>}
          {usernameMessage && <div className="success-text">{usernameMessage}</div>}
        </div>

        <div className="sidebar-section" onMouseEnter={fetchHistory}>
          <div className="small-muted">History</div>

          <div className="history-list">
            {history.length === 0 && <div className="small-muted">No history</div>}
            {history.map((h) => (
              <div
                key={h.id}
                className="history-item"
                onClick={() => {
                  setQuestion(h.question);
                  closeSidebar();
                }}
              >
                {h.question}
              </div>
            ))}
          </div>
        </div>

        <button className="logout-button" onClick={logout}>
          Logout
        </button>
      </div>

      <div className="header">
        <h1 className="brand">AKTUbot</h1>

        <p>
          AI-powered academic assistant for notes,
          syllabus and PYQs.
        </p>

        <p>
          Welcome, {user.username}
        </p>
      </div>

      <div className="card">

        <select
          className="subject-select"
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
        >
          <option value="DBMS">DBMS</option>
          <option value="OS">Operating System (OS)</option>
          <option value="CN">Computer Networks (CN)</option>
          <option value="COA">Computer Organization (COA)</option>
          <option value="Python">Python</option>
          <option value="AI">Artificial Intelligence (AI)</option>
          <option value="ML">Machine Learning (ML)</option>
        </select>

        <textarea
          placeholder={`Ask anything about ${selectedSubject}...`}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button onClick={askQuestion}>
          Ask Question
        </button>

      </div>

      {loading && (
        <div className="answer-card">
          <p>Thinking...</p>
        </div>
      )}

      {answer && (
        <div className="answer-card">

          <h2>Answer</h2>

          <div className="answer-content">
           <ReactMarkdown remarkPlugins={[remarkGfm]}>
           {answer}
           </ReactMarkdown>
          </div>

          <h3>Sources</h3>

          <div className="sources">

            {sources.map((source, index) => (
              <div key={index} className="source-item">
                <span className="source-chip">{source}</span>
              </div>
            ))}

          </div>

        </div>
      )}
    </div>
  );
}

export default App;