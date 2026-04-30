"use client";

import Link from "next/link";
import { useState } from "react";
import { BackendClient } from "../../shared/frontend_api_client";

const api = new BackendClient({ baseUrl: "http://localhost:8000" });

export default function HomePage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState("");
  const [essayItems, setEssayItems] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  async function handleLogin() {
    try {
      const result = await api.login(email, password);
      api.setToken(result.access_token);
      setToken(result.access_token);
      setStatus("Logged in");
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
  }

  async function loadEssayReviews() {
    try {
      api.setToken(token);
      const result = await api.getEssayReviewItems();
      setEssayItems(result.items);
      setStatus(`Loaded ${result.items.length} essay review item(s)`);
    } catch (err: any) {
      setStatus(err.message || "Failed to load essay reviews");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Teacher Dashboard</h1>

      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        <Link href="/question-bank">Question Bank</Link>
        <Link href="/roster">Roster</Link>
        <Link href="/essay-reviews">Essay Reviews</Link>
      </div>

      <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>Login</h2>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <br />
        <br />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
        />
        <br />
        <br />
        <button onClick={handleLogin}>Login</button>
      </section>

      <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>Essay Review Queue</h2>
        <button onClick={loadEssayReviews} disabled={!token}>
          Load Essay Review Items
        </button>
        <ul>
          {essayItems.map((item) => (
            <li key={item.review_id} style={{ marginTop: 12 }}>
              <strong>Review #{item.review_id}</strong>
              <div>Question: {item.prompt_md}</div>
              <div>Student answer: {item.student_answer}</div>
              <div>Proposed score: {item.proposed_score}</div>
            </li>
          ))}
        </ul>
      </section>

      <p>{status}</p>
    </main>
  );
}
