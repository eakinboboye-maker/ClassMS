"use client";

import { useState } from "react";
import { BackendClient, EssayReviewItem } from "../../lib/backendClient";

const api = new BackendClient({ baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000" });

export default function EssayReviewsPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState("");
  const [items, setItems] = useState<EssayReviewItem[]>([]);
  const [status, setStatus] = useState("");

  async function login() {
    try {
      const auth = await api.login(email, password);
      api.setToken(auth.access_token);
      setToken(auth.access_token);
      setStatus("Logged in");
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
  }

  async function loadItems() {
    try {
      api.setToken(token);
      const result = await api.getEssayReviewItems();
      setItems(result.items);
      setStatus(`Loaded ${result.items.length} review item(s)`);
    } catch (err: any) {
      setStatus(err.message || "Failed to load items");
    }
  }

  async function resolveReview(reviewId: number, finalScore: number) {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/grading/reviews/${reviewId}/resolve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          approved: true,
          final_score: finalScore,
          reviewer_comment: "Reviewed from dashboard",
        }),
      });
      if (!res.ok) throw new Error(`Resolve failed: ${res.status}`);
      setStatus(`Resolved review ${reviewId}`);
      await loadItems();
    } catch (err: any) {
      setStatus(err.message || "Resolve failed");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Essay Review Queue</h1>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <br /><br />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        <br /><br />
        <button onClick={login}>Login</button>
        <button onClick={loadItems} disabled={!token} style={{ marginLeft: 8 }}>
          Load Review Items
        </button>
      </div>

      {items.map((item) => (
        <div
          key={item.review_id}
          style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}
        >
          <h3>Review #{item.review_id}</h3>
          <p><strong>Question:</strong> {item.prompt_md}</p>
          <p><strong>Student answer:</strong> {item.student_answer}</p>
          <p><strong>AI proposed score:</strong> {item.proposed_score}</p>
          <p><strong>Confidence:</strong> {item.confidence}</p>
          <p><strong>Max marks:</strong> {item.max_marks}</p>
          <button onClick={() => resolveReview(item.review_id, item.proposed_score ?? 0)}>
            Approve Proposed Score
          </button>
        </div>
      ))}

      <p>{status}</p>
    </main>
  );
}
