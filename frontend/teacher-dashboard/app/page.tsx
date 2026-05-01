"use client";

import { useState } from "react";

export default function HomePage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [status, setStatus] = useState("Use this dashboard to manage questions, rosters, and reviews.");

  function handleLogin() {
    setStatus(`Login submitted for ${email}. Connect this to your existing auth flow.`);
  }

  return (
    <main>
      <h1 className="page-title">Teacher Dashboard</h1>
      <p className="page-subtitle">
        Manage classroom content, upload rosters, review essay grading, and publish learning materials.
      </p>

      <section className="card card-accent">
        <h2 className="card-title">Login</h2>
        <label className="label">Email</label>
        <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <div className="spacer-12" />
        <label className="label">Password</label>
        <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        <div className="button-row">
          <button className="btn btn-primary" onClick={handleLogin}>Login</button>
        </div>
      </section>

      <div className="grid-2">
        <section className="card">
          <h2 className="card-title">Quick Actions</h2>
          <p className="kv"><strong>Question Bank:</strong> parse, preview, and publish questions.</p>
          <p className="kv"><strong>Roster:</strong> create users and enroll them into sections.</p>
          <p className="kv"><strong>Essay Reviews:</strong> approve AI-assisted grading decisions.</p>
          <div className="button-row">
            <a className="btn btn-primary" href="/question-bank">Open Question Bank</a>
            <a className="btn btn-secondary" href="/roster">Open Roster</a>
          </div>
        </section>

        <section className="card">
          <h2 className="card-title">System Status</h2>
          <div className="notice notice-info">{status}</div>
          <div className="spacer-12" />
          <span className="badge">Teacher</span>
          <span className="badge">Uploads</span>
          <span className="badge">Reviews</span>
          <span className="badge">Publishing</span>
        </section>
      </div>
    </main>
  );
}
