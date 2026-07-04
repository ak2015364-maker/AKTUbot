import Login from "./Login";
import Signup from "./Signup";
import { useState } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function App() {
  const user = JSON.parse(localStorage.getItem("user"));

  const [showSignup, setShowSignup] = useState(false);

  const [showSidebar, setShowSidebar] = useState(false);
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("theme") === "dark"
  );
  const [history, setHistory] = useState([]);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState("DBMS");

  const getSourceDownloadUrl = (source) =>
    `http://127.0.0.1:8000/download-pdf/${encodeURIComponent(source)}`;

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask-rag", {
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

  const toggleTheme = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem("theme", next ? "dark" : "light");
    if (next) document.body.classList.add("dark");
    else document.body.classList.remove("dark");
  };

  const fetchHistory = async () => {
    if (!user) return;
    try {
      const res = await axios.get(`http://127.0.0.1:8000/history/${user.id}`);
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
    window.location.reload();
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
                <a
                  href={getSourceDownloadUrl(source)}
                  className="source-chip"
                  target="_blank"
                  rel="noopener noreferrer"
                  download={source}
                  aria-label={`Download PDF ${source}`}
                >
                  {source}
                </a> 
                <span className="source-hint">click to access PDF</span>
              </div>
            ))}

          </div>

        </div>
      )}
    </div>
  );
}

export default App;