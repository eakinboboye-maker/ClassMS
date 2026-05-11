"use client";

import { useState } from "react";
import { fetchEssayQueue } from "../../lib/dashboard-api";

export default function EssayReviewsPage() {
  const [token, setToken] = useState("");
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState("Load the live essay review queue from the backend.");

  async function loadQueue() {
    try {
      const payload = await fetchEssayQueue(token);
      const rows = payload.items || payload.reviews || payload || [];
      setItems(Array.isArray(rows) ? rows : []);
      setStatus(`Loaded ${Array.isArray(rows) ? rows.length : 0} review item(s).`);
    } catch (err: any) {
      setStatus(err.message || "Failed to load queue");
    }
  }

  return (
    <main>
      <h1 className="page-title">Essay Review Queue</h1>
      <p className="page-subtitle">Approve, revise, and publish AI-assisted grading decisions.</p>

      <section className="card card-accent">
        <h2 className="card-title">Teacher Access</h2>
        <label className="label">Teacher access token</label>
        <input className="input" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste teacher JWT" />
        <div className="button-row">
          <button className="btn btn-primary" onClick={loadQueue}>Load Queue</button>
        </div>
        <div className="notice notice-info">{status}</div>
      </section>

      {items.map((item, idx) => (
        <section key={item.review_id || item.id || idx} className="card">
          <h2 className="card-title">Review #{item.review_id || item.id || idx + 1}</h2>
          <div className="kv"><strong>Question:</strong> {item.prompt || item.question_prompt || "—"}</div>
          <div className="kv"><strong>Student answer:</strong> {item.answer_text || item.student_answer || "—"}</div>
          <div className="kv"><strong>AI proposed score:</strong> {item.proposed_score ?? item.awarded_marks ?? "—"} / {item.max_marks ?? "—"}</div>
          <div className="kv"><strong>Confidence:</strong> {item.confidence ?? "—"}</div>
          <div className="button-row">
            <button className="btn btn-success">Approve</button>
            <button className="btn btn-warning">Adjust Score</button>
            <button className="btn btn-secondary">Skip</button>
          </div>
        </section>
      ))}
    </main>
  );
}
