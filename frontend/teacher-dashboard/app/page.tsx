"use client";

import { useState } from "react";
import { loginTeacher, fetchMe } from "../lib/dashboard-api";

export default function HomePage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [status, setStatus] = useState("Sign in to use the live dashboard.");
  const [token, setToken] = useState("");
  const [me, setMe] = useState<any>(null);

  async function handleLogin() {
    try {
      const auth = await loginTeacher(email, password);
      setToken(auth.access_token);
      const profile = await fetchMe(auth.access_token);
      setMe(profile);
      setStatus(`Logged in as ${profile.full_name}`);
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
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
        <div className={`notice ${me ? "notice-success" : "notice-info"}`}>{status}</div>
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
            <a className="btn btn-warning" href="/essay-reviews">Open Essay Reviews</a>
          </div>
        </section>

        <section className="card">
          <h2 className="card-title">Live Session</h2>
          {me ? (
            <>
              <div className="kv"><strong>Name:</strong> {me.full_name}</div>
              <div className="kv"><strong>Email:</strong> {me.email}</div>
              <div className="kv"><strong>Role:</strong> {me.role}</div>
              <div className="badge">Authenticated</div>
              {token ? <div className="badge">Token ready</div> : null}
            </>
          ) : (
            <div className="notice notice-info">No active session yet.</div>
          )}
        </section>
      </div>
    </main>
  );
}
