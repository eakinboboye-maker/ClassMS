"use client";

import { useState } from "react";

export default function RosterPage() {
  const [token, setToken] = useState("");
  const [usersCsv, setUsersCsv] = useState("");
  const [enrollmentJson, setEnrollmentJson] = useState(`[{"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"}]`);
  const [status, setStatus] = useState("Parse user rows, then publish users and enrollments.");

  return (
    <main>
      <h1 className="page-title">Roster Import</h1>
      <p className="page-subtitle">Load student users first, then enroll them into the correct course section.</p>

      <section className="card card-accent">
        <h2 className="card-title">Teacher Access</h2>
        <label className="label">Teacher access token</label>
        <input
          className="input"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Paste teacher JWT"
        />
      </section>

      <section className="card">
        <h2 className="card-title">1. Student Users CSV</h2>
        <label className="label">Paste users CSV</label>
        <textarea
          className="textarea"
          value={usersCsv}
          onChange={(e) => setUsersCsv(e.target.value)}
          placeholder="Paste student_users_template.csv content here"
        />
        <div className="button-row">
          <button className="btn btn-primary" onClick={() => setStatus("Parsed student users.")}>Parse Users</button>
          <button className="btn btn-success" onClick={() => setStatus("Created or updated users.")}>Create / Update Users</button>
        </div>
      </section>

      <section className="card">
        <h2 className="card-title">2. Course Enrollment Rows</h2>
        <label className="label">Paste enrollment JSON rows</label>
        <textarea
          className="textarea"
          value={enrollmentJson}
          onChange={(e) => setEnrollmentJson(e.target.value)}
          placeholder='Paste JSON rows converted from course_enrollment_template.csv'
        />
        <div className="button-row">
          <button className="btn btn-primary" onClick={() => setStatus("Parsed enrollment rows.")}>Parse Enrollment</button>
          <button className="btn btn-success" onClick={() => setStatus("Published enrollment rows.")}>Enroll into Section</button>
        </div>
        <div className="notice notice-info">{status}</div>
      </section>
    </main>
  );
}
