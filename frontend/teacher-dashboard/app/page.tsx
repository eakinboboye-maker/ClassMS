"use client";

import Link from "next/link";
import { useState } from "react";
import { apiFetch, login } from "../lib/api";

export default function HomePage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState("");
  const [essayItems, setEssayItems] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  async function handleLogin() {
    try {
      const result = await login(email, password);
      setToken(result.access_token);
      setStatus("Logged in");
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
  }

  async function loadEssayReviews() {
    try {
      const result = await apiFetch("/api/grading/reviews/essay-items", token);
      setEssayItems(result.items || []);
      setStatus(`Loaded ${result.items.length} essay review item(s)`);
    } catch (err: any) {
      setStatus(err.message || "Failed to load essay reviews");
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Teacher Dashboard</h1>
        <p className="muted">Manage questions, rosters, reviews, and classroom workflows.</p>
        <div className="row">
          <Link href="/question-bank">Open Question Bank</Link>
          <Link href="/roster">Open Roster Import</Link>
          <Link href="/essay-reviews">Open Essay Reviews</Link>
        </div>
      </div>

      <div className="card">
        <h2>Login</h2>
        <div className="row">
          <div style={{ flex: 1, minWidth: 260 }}>
            <label>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          </div>
          <div style={{ flex: 1, minWidth: 260 }}>
            <label>Password</label>
            <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
          </div>
        </div>
        <div style={{ marginTop: 12 }}>
          <button onClick={handleLogin}>Login</button>
        </div>
      </div>

      <div className="card">
        <h2>Essay Review Queue</h2>
        <button onClick={loadEssayReviews} disabled={!token}>Load Essay Review Items</button>
        <div style={{ marginTop: 12 }}>
          {essayItems.map((item) => (
            <div key={item.review_id} className="card" style={{ marginBottom: 12 }}>
              <strong>Review #{item.review_id}</strong>
              <div>Question: {item.prompt_md}</div>
              <div>Student answer: {item.student_answer}</div>
              <div>Proposed score: {item.proposed_score}</div>
            </div>
          ))}
        </div>
      </div>

      <p>{status}</p>
    </main>
  );
}
