"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/imports-api";
import { loadTeacherSession } from "../../lib/auth";

export default function RosterPage() {
  const [usersCsv, setUsersCsv] = useState("");
  const [usersPreview, setUsersPreview] = useState<any[]>([]);
  const [enrollmentJson, setEnrollmentJson] = useState(`[{"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"}]`);
  const [enrollmentPreview, setEnrollmentPreview] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const session = loadTeacherSession();
    if (!session?.token) setStatus("No teacher session found. Please sign in on the Home page.");
  }, []);

  async function parseUsers() {
    try {
      const result = await apiFetch("/api/imports/users/parse-csv", { method: "POST", body: JSON.stringify({ text: usersCsv }) });
      setUsersPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} user row(s)`);
    } catch (err: any) { setStatus(err.message || "User parse failed"); }
  }

  async function createUsers() {
    try {
      const result = await apiFetch("/api/imports/users/bulk-create", { method: "POST", body: JSON.stringify({ users: usersPreview, default_password: "changeme123", skip_existing: true }) });
      setStatus(`Created ${result.created_count} user(s), skipped ${result.skipped_count}`);
    } catch (err: any) { setStatus(err.message || "User creation failed"); }
  }

  async function parseEnrollment() {
    try {
      const rows = JSON.parse(enrollmentJson);
      const result = await apiFetch("/api/imports/enrollment/parse", { method: "POST", body: JSON.stringify({ rows }) });
      setEnrollmentPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} enrollment row(s)`);
    } catch (err: any) { setStatus(err.message || "Enrollment parse failed"); }
  }

  async function publishEnrollment() {
    try {
      const result = await apiFetch("/api/imports/enrollment/publish", { method: "POST", body: JSON.stringify({ rows: enrollmentPreview }) });
      setStatus(`Enrolled ${result.enrolled_count}, skipped ${result.skipped_count}`);
    } catch (err: any) { setStatus(err.message || "Enrollment publish failed"); }
  }

  return (
    <main>
      <h1 className="page-title">Roster Import</h1>
      <p className="page-subtitle">Load student users first, then enroll them into the correct course section.</p>
      <section className="card card-accent"><h2 className="card-title">Teacher Session</h2><div className="notice notice-info">{status || "Signed-in teacher session will be used automatically."}</div></section>
      <section className="card"><h2 className="card-title">1. Student Users CSV</h2><label className="label">Paste users CSV</label><textarea className="textarea" value={usersCsv} onChange={(e) => setUsersCsv(e.target.value)} placeholder="Paste student_users_template.csv content here" /><div className="button-row"><button className="btn btn-primary" onClick={parseUsers}>Parse Users</button><button className="btn btn-success" onClick={createUsers} disabled={usersPreview.length === 0}>Create / Update Users</button></div></section>
      <section className="card"><h2 className="card-title">2. Course Enrollment Rows</h2><label className="label">Paste enrollment JSON rows</label><textarea className="textarea" value={enrollmentJson} onChange={(e) => setEnrollmentJson(e.target.value)} /><div className="button-row"><button className="btn btn-primary" onClick={parseEnrollment}>Parse Enrollment</button><button className="btn btn-success" onClick={publishEnrollment} disabled={enrollmentPreview.length === 0}>Enroll into Section</button></div></section>
    </main>
  );
}
