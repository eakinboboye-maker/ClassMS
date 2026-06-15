"use client";

import { useMemo, useState } from "react";
import { BackendClient, EssayReviewItem, apiBase } from "../lib/api";

const api = new BackendClient({ baseUrl: apiBase });
type TabKey = "overview" | "essay" | "gradebook" | "incidents";

export default function TeacherDashboard() {
  const [tab, setTab] = useState<TabKey>("overview");
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState("");
  const [status, setStatus] = useState("Not connected");
  const [essayItems, setEssayItems] = useState<EssayReviewItem[]>([]);
  const [gradebookRows, setGradebookRows] = useState<any[]>([]);
  const [incidentRows, setIncidentRows] = useState<any[]>([]);
  const [assessmentFilter, setAssessmentFilter] = useState("");

  const stats = useMemo(() => ({
    essayQueue: essayItems.length,
    gradeRows: gradebookRows.length,
    incidents: incidentRows.length,
    backend: apiBase,
  }), [essayItems, gradebookRows, incidentRows]);

  async function login() {
    try {
      const auth = await api.login(email, password);
      api.setToken(auth.access_token);
      setToken(auth.access_token);
      setStatus("Connected to backend successfully.");
    } catch (err: any) {
      setStatus(err.message || "Login failed");
    }
  }

  async function loadEssayReviews() {
    try {
      api.setToken(token);
      const result = await api.getEssayReviewItems();
      setEssayItems(result.items || []);
      setStatus(`Loaded ${result.items?.length || 0} essay review item(s).`);
      setTab("essay");
    } catch (err: any) {
      setStatus(err.message || "Failed to load essay reviews");
    }
  }

  async function approveEssay(item: EssayReviewItem) {
    try {
      api.setToken(token);
      await api.resolveEssayReview(item.review_id, item.proposed_score ?? 0);
      await loadEssayReviews();
      setStatus(`Approved review #${item.review_id}.`);
    } catch (err: any) {
      setStatus(err.message || "Failed to approve review");
    }
  }

  async function loadGradebook() {
    try {
      api.setToken(token);
      const query = assessmentFilter ? `assessment_id=${encodeURIComponent(assessmentFilter)}` : "";
      const result = await api.getGradebook(query);
      setGradebookRows(result.rows || []);
      setStatus(`Loaded ${result.rows?.length || 0} gradebook row(s).`);
      setTab("gradebook");
    } catch (err: any) {
      setStatus(err.message || "Failed to load gradebook");
    }
  }

  async function loadIncidents() {
    try {
      api.setToken(token);
      const query = assessmentFilter ? `assessment_id=${encodeURIComponent(assessmentFilter)}` : "";
      const result = await api.getIncidentDashboard(query);
      setIncidentRows(result.rows || []);
      setStatus(`Loaded ${result.rows?.length || 0} incident row(s).`);
      setTab("incidents");
    } catch (err: any) {
      setStatus(err.message || "Failed to load incidents");
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">ClassLite<small>Teacher Console</small></div>
        <div className="nav">
          {(["overview", "essay", "gradebook", "incidents"] as TabKey[]).map((key) => (
            <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>
              {key === "overview" ? "Overview" : key === "essay" ? "Essay Review" : key === "gradebook" ? "Gradebook" : "Incidents"}
            </button>
          ))}
        </div>
        <div style={{ marginTop: 24 }} className="notice">
          <div><strong>Backend</strong></div>
          <div style={{ marginTop: 8, wordBreak: "break-word" }}>{stats.backend}</div>
        </div>
      </aside>
      <main className="main">
        <div className="topbar">
          <div>
            <h1 className="h1">Teacher Dashboard</h1>
            <div className="subtitle">Polished Vercel-ready interface for review, gradebook, and monitoring.</div>
          </div>
          <span className="badge">{token ? "Authenticated" : "Not logged in"}</span>
        </div>

        <div className="grid cards" style={{ marginBottom: 16 }}>
          <div className="card"><h3>Essay queue</h3><div className="stat">{stats.essayQueue}</div></div>
          <div className="card"><h3>Gradebook rows</h3><div className="stat">{stats.gradeRows}</div></div>
          <div className="card"><h3>Incidents</h3><div className="stat">{stats.incidents}</div></div>
        </div>

        <div className="card" style={{ marginBottom: 16 }}>
          <div className="row">
            <div className="field"><label className="label">Email</label><input className="input" value={email} onChange={(e)=>setEmail(e.target.value)} /></div>
            <div className="field"><label className="label">Password</label><input className="input" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} /></div>
            <div className="field"><label className="label">Assessment filter</label><input className="input" value={assessmentFilter} onChange={(e)=>setAssessmentFilter(e.target.value)} placeholder="Optional assessment id" /></div>
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="btn" onClick={login}>Login</button>
            <button className="btn secondary" disabled={!token} onClick={loadEssayReviews}>Load essay reviews</button>
            <button className="btn secondary" disabled={!token} onClick={loadGradebook}>Load gradebook</button>
            <button className="btn secondary" disabled={!token} onClick={loadIncidents}>Load incidents</button>
          </div>
          <div style={{ marginTop: 12 }} className="badge">{status}</div>
        </div>

        {tab === "overview" && (
          <div className="grid cards">
            <div className="card"><h3>Review workflow</h3><p className="subtitle">Load essay items, inspect AI proposals, and approve the score with one click.</p></div>
            <div className="card"><h3>Gradebook</h3><p className="subtitle">Filter by assessment, then inspect awarded vs maximum marks for each attempt.</p></div>
            <div className="card"><h3>Incident visibility</h3><p className="subtitle">Track heartbeat/replay problems and review exported incident data from the backend.</p></div>
          </div>
        )}

        {tab === "essay" && (
          <div className="grid">
            {essayItems.length === 0 ? <div className="card empty">No essay reviews waiting.</div> : essayItems.map((item) => (
              <div key={item.review_id} className="card">
                <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
                  <h3>Review #{item.review_id}</h3>
                  <span className="badge">Confidence {item.confidence ?? "—"}</span>
                </div>
                <p className="subtitle">Attempt #{item.attempt_id} · Question #{item.question_id} · Max {item.max_marks}</p>
                <div className="review-answer" style={{ marginTop: 12 }}>{item.student_answer || "No answer text"}</div>
                <div className="row" style={{ marginTop: 12 }}>
                  <span className="badge">AI proposed: {item.proposed_score ?? "—"}</span>
                  {(item.flags || []).map((flag) => <span key={flag} className="badge">{flag}</span>)}
                </div>
                <div className="row" style={{ marginTop: 14 }}>
                  <button className="btn success" onClick={() => approveEssay(item)}>Approve proposed score</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {tab === "gradebook" && (
          <div className="card table-wrap">
            {gradebookRows.length === 0 ? <div className="empty">No gradebook rows loaded.</div> : (
              <table className="table">
                <thead><tr><th>User</th><th>Attempt</th><th>Assessment</th><th>Score</th><th>Published</th></tr></thead>
                <tbody>
                  {gradebookRows.map((row, idx) => (
                    <tr key={idx}><td>{row.user_id}</td><td>{row.attempt_id}</td><td>{row.assessment_id}</td><td>{row.total_awarded} / {row.total_max}</td><td>{String(row.published)}</td></tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {tab === "incidents" && (
          <div className="card table-wrap">
            {incidentRows.length === 0 ? <div className="empty">No incidents loaded.</div> : (
              <table className="table">
                <thead><tr><th>Incident</th><th>Attempt</th><th>User</th><th>Type</th><th>Created</th></tr></thead>
                <tbody>
                  {incidentRows.map((row, idx) => (
                    <tr key={idx}><td>{row.incident_id}</td><td>{row.attempt_id}</td><td>{row.user_id}</td><td>{row.incident_type}</td><td>{row.created_at}</td></tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
