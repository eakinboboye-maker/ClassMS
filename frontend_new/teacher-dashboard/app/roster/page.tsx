"use client";

import { useState } from "react";
import { apiFetch } from "../../lib/api";

export default function RosterPage() {
  const [token, setToken] = useState("");
  const [usersCsv, setUsersCsv] = useState("");
  const [usersPreview, setUsersPreview] = useState<any[]>([]);
  const [enrollmentJson, setEnrollmentJson] = useState('[{"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"}]');
  const [enrollmentPreview, setEnrollmentPreview] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  async function parseUsers() {
    try {
      const result = await apiFetch("/api/imports/users/parse-csv", token, {
        method: "POST",
        body: JSON.stringify({ text: usersCsv }),
      });
      setUsersPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} user row(s)`);
    } catch (err: any) {
      setStatus(err.message || "User parse failed");
    }
  }

  async function createUsers() {
    try {
      const result = await apiFetch("/api/imports/users/bulk-create", token, {
        method: "POST",
        body: JSON.stringify({
          users: usersPreview,
          default_password: "changeme123",
          skip_existing: true
        }),
      });
      setStatus(`Created ${result.created_count} user(s), skipped ${result.skipped_count}`);
    } catch (err: any) {
      setStatus(err.message || "User creation failed");
    }
  }

  async function parseEnrollment() {
    try {
      const rows = JSON.parse(enrollmentJson);
      const result = await apiFetch("/api/imports/enrollment/parse", token, {
        method: "POST",
        body: JSON.stringify({ rows }),
      });
      setEnrollmentPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} enrollment row(s)`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment parse failed");
    }
  }

  async function publishEnrollment() {
    try {
      const result = await apiFetch("/api/imports/enrollment/publish", token, {
        method: "POST",
        body: JSON.stringify({ rows: enrollmentPreview }),
      });
      setStatus(`Enrolled ${result.enrolled_count}, skipped ${result.skipped_count}`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment publish failed");
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Roster Import</h1>
        <p className="muted">Parse student users, create accounts, then publish enrollments.</p>
      </div>

      <div className="card">
        <label>Teacher access token</label>
        <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste teacher JWT" style={{ marginTop: 8 }} />
      </div>

      <div className="card">
        <h2>1. Parse Student Users CSV</h2>
        <textarea value={usersCsv} onChange={(e) => setUsersCsv(e.target.value)} placeholder="Paste student_users_template.csv content here" style={{ minHeight: 220 }} />
        <div className="row" style={{ marginTop: 12 }}>
          <button onClick={parseUsers}>Parse Users</button>
          <button onClick={createUsers} disabled={usersPreview.length === 0}>Create / Update Users</button>
        </div>
        {usersPreview.length > 0 && <pre>{JSON.stringify(usersPreview, null, 2)}</pre>}
      </div>

      <div className="card">
        <h2>2. Parse Course Enrollment Rows</h2>
        <textarea value={enrollmentJson} onChange={(e) => setEnrollmentJson(e.target.value)} placeholder='Paste JSON rows converted from course_enrollment_template.csv' style={{ minHeight: 220 }} />
        <div className="row" style={{ marginTop: 12 }}>
          <button onClick={parseEnrollment}>Parse Enrollment</button>
          <button onClick={publishEnrollment} disabled={enrollmentPreview.length === 0}>Enroll into Section</button>
        </div>
        {enrollmentPreview.length > 0 && <pre>{JSON.stringify(enrollmentPreview, null, 2)}</pre>}
      </div>

      <p>{status}</p>
    </main>
  );
}
