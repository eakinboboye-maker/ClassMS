"use client";

import { useState } from "react";
import { apiFetch } from "../../lib/imports-api";

type GenericRow = Record<string, any>;

export default function RosterPage() {
  const [token, setToken] = useState("");

  const [usersCsv, setUsersCsv] = useState("");
  const [usersXlsxRowsJson, setUsersXlsxRowsJson] = useState(`[
  {"Reg No.":"EEE/2026/001","Names":"Amina Yusuf","Email Address":"amina@school.edu","Session":"2026/2027"},
  {"Reg No.":"EEE/2026/002","Names":"David Ade","Email Address":"david@school.edu","Session":"2026/2027"}
]`);
  const [usersPreview, setUsersPreview] = useState<any[]>([]);

  const [enrollmentJson, setEnrollmentJson] = useState(`[
  {"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"}
]`);
  const [enrollmentSheetRowsJson, setEnrollmentSheetRowsJson] = useState(`[
  {"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"},
  {"Reg No.":"EEE/2026/002","Course Code":"EEE355","Section":"A","Session":"2026/2027"}
]`);
  const [enrollmentPreview, setEnrollmentPreview] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  async function parseUsersCsv() {
    try {
      const result = await apiFetch("/api/imports/users/parse-csv", {
        method: "POST",
        headers: {
    	  Authorization: `Bearer ${token}`,
  	},
        body: JSON.stringify({ text: usersCsv }),
      });
      setUsersPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} user row(s) from CSV`);
    } catch (err: any) {
      setStatus(err.message || "User CSV parse failed");
    }
  }

  async function parseUsersXlsxRows() {
    try {
      const rows: GenericRow[] = JSON.parse(usersXlsxRowsJson);
      const result = await apiFetch("/api/imports/users/parse-xlsx-rows", {
        method: "POST",
        headers: {
    	  Authorization: `Bearer ${token}`,
  	},
        body: JSON.stringify({ rows }),
      });
      setUsersPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} user row(s) from XLSX rows`);
    } catch (err: any) {
      setStatus(err.message || "User XLSX rows parse failed");
    }
  }

  async function createUsers() {
    try {
      const result = await apiFetch("/api/imports/users/bulk-create", {
        method: "POST",
        headers: {
    	  Authorization: `Bearer ${token}`,
  	},
        body: JSON.stringify({
          users: usersPreview,
          default_password: "changeme123",
          skip_existing: true,
        }),
      });
      setStatus(`Created ${result.created_count} user(s), skipped ${result.skipped_count}`);
    } catch (err: any) {
      setStatus(err.message || "User creation failed");
    }
  }

  async function parseEnrollmentJson() {
    try {
      const rows = JSON.parse(enrollmentJson);
      const result = await apiFetch("/api/imports/enrollment/parse", {
        method: "POST",
        headers: {
    	  Authorization: `Bearer ${token}`,
  	},
        body: JSON.stringify({ rows }),
      });
      setEnrollmentPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} enrollment row(s) from JSON`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment JSON parse failed");
    }
  }

  async function parseEnrollmentSheetRows() {
    try {
      const rows = JSON.parse(enrollmentSheetRowsJson);
      const result = await apiFetch("/api/imports/enrollment/parse", {
        method: "POST",
        headers: {
    	  Authorization: `Bearer ${token}`,
  	},
        body: JSON.stringify({ rows }),
      });
      setEnrollmentPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} enrollment row(s) from CSV/XLSX-style rows`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment sheet rows parse failed");
    }
  }

  async function publishEnrollment() {
    try {
      const result = await apiFetch("/api/imports/enrollment/publish", {
        method: "POST",
        headers: {
    	  Authorization: `Bearer ${token}`,
  	},
        body: JSON.stringify({ rows: enrollmentPreview }),
      });
      setStatus(`Enrolled ${result.enrolled_count}, skipped ${result.skipped_count}`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment publish failed");
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <h1>Roster Import</h1>
      <p>Roster input can be CSV/XLSX. Enrollment publishes as JSON, but you can also paste CSV/XLSX-style row JSON and convert it first.</p>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <label>Teacher access token</label>
        <input
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Paste teacher JWT"
          style={{ width: "100%", marginTop: 8 }}
        />
      </div>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>1. Student Users from CSV</h2>
        <textarea
          value={usersCsv}
          onChange={(e) => setUsersCsv(e.target.value)}
          placeholder="Paste CSV content here"
          style={{ width: "100%", minHeight: 180 }}
        />
        <div style={{ marginTop: 12 }}>
          <button onClick={parseUsersCsv}>Parse Users CSV</button>
        </div>
      </div>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>2. Student Users from XLSX Rows JSON</h2>
        <p>Paste rows extracted from an uploaded Excel file on the frontend.</p>
        <textarea
          value={usersXlsxRowsJson}
          onChange={(e) => setUsersXlsxRowsJson(e.target.value)}
          style={{ width: "100%", minHeight: 180 }}
        />
        <div style={{ marginTop: 12 }}>
          <button onClick={parseUsersXlsxRows}>Parse Users XLSX Rows</button>
          <button onClick={createUsers} disabled={usersPreview.length === 0} style={{ marginLeft: 8 }}>
            Create / Update Users
          </button>
        </div>
        {usersPreview.length > 0 && (
          <pre style={{ marginTop: 12, whiteSpace: "pre-wrap" }}>{JSON.stringify(usersPreview, null, 2)}</pre>
        )}
      </div>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>3. Enrollment from JSON</h2>
        <textarea
          value={enrollmentJson}
          onChange={(e) => setEnrollmentJson(e.target.value)}
          style={{ width: "100%", minHeight: 180 }}
        />
        <div style={{ marginTop: 12 }}>
          <button onClick={parseEnrollmentJson}>Parse Enrollment JSON</button>
        </div>
      </div>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>4. Enrollment from CSV/XLSX-style Rows JSON</h2>
        <p>Paste rows extracted from CSV/XLSX, then convert to the JSON payload preview before publish.</p>
        <textarea
          value={enrollmentSheetRowsJson}
          onChange={(e) => setEnrollmentSheetRowsJson(e.target.value)}
          style={{ width: "100%", minHeight: 180 }}
        />
        <div style={{ marginTop: 12 }}>
          <button onClick={parseEnrollmentSheetRows}>Parse Enrollment Sheet Rows</button>
          <button onClick={publishEnrollment} disabled={enrollmentPreview.length === 0} style={{ marginLeft: 8 }}>
            Publish Enrollment JSON
          </button>
        </div>
        {enrollmentPreview.length > 0 && (
          <pre style={{ marginTop: 12, whiteSpace: "pre-wrap" }}>{JSON.stringify(enrollmentPreview, null, 2)}</pre>
        )}
      </div>

      <p>{status}</p>
    </main>
  );
}
