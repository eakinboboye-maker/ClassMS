"use client";

import { useEffect, useState } from "react";
import { loginTeacher, fetchMe } from "../lib/dashboard-api";
import { clearTeacherSession, loadTeacherSession, saveTeacherSession } from "../lib/auth";

export default function HomePage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [status, setStatus] = useState("Sign in to use the live dashboard.");
  const [me, setMe] = useState<any>(null);

  useEffect(() => {
    const session = loadTeacherSession();
    if (session?.user) {
      setMe(session.user);
      setStatus(`Signed in as ${session.user.full_name}`);
    }
  }, []);

  async function handleLogin() {
    try {
      const auth = await loginTeacher(email, password);
      const profile = await fetchMe(auth.access_token);
      saveTeacherSession({ token: auth.access_token, user: profile });
      setMe(profile);
      setStatus(`Signed in as ${profile.full_name}`);
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
  }

  function handleLogout() {
    clearTeacherSession();
    setMe(null);
    setStatus("Signed out.");
  }

  return (
    <main>
      <h1 className="page-title">Teacher Dashboard</h1>
      <p className="page-subtitle">Manage classroom content, upload rosters, review essay grading, and publish learning materials.</p>
      <section className="card card-accent">
        <h2 className="card-title">Login</h2>
        <label className="label">Email</label>
        <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <div className="spacer-12" />
        <label className="label">Password</label>
        <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        <div className="button-row">
          <button className="btn btn-primary" onClick={handleLogin}>Login</button>
          <button className="btn btn-secondary" onClick={handleLogout}>Logout</button>
        </div>
        <div className={`notice ${me ? "notice-success" : "notice-info"}`}>{status}</div>
      </section>
    </main>
  );
}
