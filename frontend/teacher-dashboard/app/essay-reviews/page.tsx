"use client";

import { useState } from "react";
import { apiFetch, login } from "../../lib/api";

export default function EssayReviewsPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState("");
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  async function doLogin() {
    try {
      const auth = await login(email, password);
      setToken(auth.access_token);
      setStatus("Logged in");
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
  }

  async function loadItems() {
    try {
      const result = await apiFetch("/api/grading/reviews/essay-items", token);
      setItems(result.items || []);
      setStatus(`Loaded ${result.items.length} review item(s)`);
    } catch (err: any) {
      setStatus(err.message || "Failed to load items");
    }
  }

  return (
    <main>
      <div className="card"><h1>Essay Reviews</h1></div>
      <div className="card">
        <div className="row">
          <div style={{ flex: 1, minWidth: 260 }}>
            <label>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div style={{ flex: 1, minWidth: 260 }}>
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button onClick={doLogin}>Login</button>
          <button onClick={loadItems} disabled={!token}>Load Review Items</button>
        </div>
      </div>
      <div className="card">
        {items.map((item) => (
          <div key={item.review_id} className="card">
            <h3>Review #{item.review_id}</h3>
            <p><strong>Question:</strong> {item.prompt_md}</p>
            <p><strong>Student answer:</strong> {item.student_answer}</p>
            <p><strong>AI proposed score:</strong> {item.proposed_score}</p>
            <p><strong>Confidence:</strong> {item.confidence}</p>
          </div>
        ))}
      </div>
      <p>{status}</p>
    </main>
  );
}
