"use client";

import { useEffect, useState } from "react";
import { fetchEssayQueue } from "../../lib/dashboard-api";
import { loadTeacherSession } from "../../lib/auth";

export default function EssayReviewsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState("Load the live essay review queue from the backend.");

  useEffect(() => {
    const session = loadTeacherSession();
    if (!session?.token) setStatus("No teacher session found. Please sign in on the Home page.");
  }, []);

  async function loadQueue() {
    try {
      const session = loadTeacherSession();
      if (!session?.token) throw new Error("No teacher session found. Please sign in on the Home page.");
      const payload = await fetchEssayQueue(session.token);
      const rows = payload.items || payload.reviews || payload || [];
      setItems(Array.isArray(rows) ? rows : []);
      setStatus(`Loaded ${Array.isArray(rows) ? rows.length : 0} review item(s).`);
    } catch (err: any) { setStatus(err.message || "Failed to load queue"); }
  }

  return (
    <main>
      <h1 className="page-title">Essay Review Queue</h1>
      <p className="page-subtitle">Approve, revise, and publish AI-assisted grading decisions.</p>
      <section className="card card-accent"><h2 className="card-title">Teacher Session</h2><div className="button-row"><button className="btn btn-primary" onClick={loadQueue}>Load Queue</button></div><div className="notice notice-info">{status}</div></section>
      {items.map((item, idx) => <section key={item.review_id || item.id || idx} className="card"><h2 className="card-title">Review #{item.review_id || item.id || idx + 1}</h2><div className="kv"><strong>Question:</strong> {item.prompt || item.question_prompt || "—"}</div><div className="kv"><strong>Student answer:</strong> {item.answer_text || item.student_answer || "—"}</div></section>)}
    </main>
  );
}
