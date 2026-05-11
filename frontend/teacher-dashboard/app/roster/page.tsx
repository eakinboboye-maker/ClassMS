"use client";

import { useState } from "react";
import { apiFetch } from "../../lib/imports-api";

export default function RosterPage() {
  const [token, setToken] = useState("");
  const [usersCsv, setUsersCsv] = useState("");
  const [usersPreview, setUsersPreview] = useState<any[]>([]);
  const [enrollmentJson, setEnrollmentJson] = useState(`[{"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"}]`);
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
        body: JSON.stringify({ users: usersPreview, default_password: "changeme123", skip_existing: true }),
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
      <h1 className="page-title">Roster Import</h1>
      <p className="page-subtitle">Load student users first, then enroll them into the correct course section.</p>

      <section className="card card-accent">
        <h2 className="card-title">Teacher Access</h2>
        <label className="label">Teacher access token</label>
        <input className="input" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste teacher JWT" />
      </section>

      <section className="card">
        <h2 className="card-title">1. Student Users CSV</h2>
        <label className="label">Paste users CSV</label>
        <textarea className="textarea" value={usersCsv} onChange={(e) => setUsersCsv(e.target.value)} placeholder="Paste student_users_template.csv content here" />
        <div className="button-row">
          <button className="btn btn-primary" onClick={parseUsers}>Parse Users</button>
          <button className="btn btn-success" onClick={createUsers} disabled={usersPreview.length === 0}>Create / Update Users</button>
        </div>
      </section>

      {usersPreview.length > 0 && (
        <section className="card">
          <h2 className="card-title">Parsed Users Preview</h2>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Matric No</th><th>Full Name</th><th>Email</th><th>Role</th></tr></thead>
              <tbody>
                {usersPreview.map((row, i) => (
                  <tr key={i}>
                    <td>{row.matric_no}</td><td>{row.full_name}</td><td>{row.email}</td><td>{row.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="card">
        <h2 className="card-title">2. Course Enrollment Rows</h2>
        <label className="label">Paste enrollment JSON rows</label>
        <textarea className="textarea" value={enrollmentJson} onChange={(e) => setEnrollmentJson(e.target.value)} placeholder='Paste JSON rows converted from course_enrollment_template.csv' />
        <div className="button-row">
          <button className="btn btn-primary" onClick={parseEnrollment}>Parse Enrollment</button>
          <button className="btn btn-success" onClick={publishEnrollment} disabled={enrollmentPreview.length === 0}>Enroll into Section</button>
        </div>
        {status ? <div className="notice notice-info">{status}</div> : null}
      </section>

      {enrollmentPreview.length > 0 && (
        <section className="card">
          <h2 className="card-title">Parsed Enrollment Preview</h2>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Reg No</th><th>Course Code</th><th>Section</th><th>Session</th></tr></thead>
              <tbody>
                {enrollmentPreview.map((row, i) => (
                  <tr key={i}>
                    <td>{row.reg_no}</td><td>{row.course_code}</td><td>{row.section}</td><td>{row.session}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}
