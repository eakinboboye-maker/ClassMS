"use client";

import { useState } from "react";
import * as XLSX from "xlsx";
import { apiFetchWithToken } from "../../lib/imports-api";

type GenericRow = Record<string, any>;

export default function RosterPage() {
  const [token, setToken] = useState("");

  const [usersCsv, setUsersCsv] = useState("");
  const [usersPreview, setUsersPreview] = useState<any[]>([]);
  const [status, setStatus] = useState("");

  const [enrollmentJson, setEnrollmentJson] = useState(`[
  {"Reg No.":"EEE/2026/001","Course Code":"EEE355","Section":"A","Session":"2026/2027"}
]`);
  const [enrollmentPreview, setEnrollmentPreview] = useState<any[]>([]);

  async function parseUsersCsv() {
    try {
      const result = await apiFetchWithToken("/api/imports/users/parse-csv", token, {
        method: "POST",
        body: JSON.stringify({ text: usersCsv }),
      });
      setUsersPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} user row(s) from CSV`);
    } catch (err: any) {
      setStatus(err.message || "User CSV parse failed");
    }
  }

  async function handleUsersExcelUpload(file: File) {
    try {
      const buf = await file.arrayBuffer();
      const workbook = XLSX.read(buf, { type: "array" });
      const firstSheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[firstSheetName];

      const rows: GenericRow[] = XLSX.utils.sheet_to_json(sheet, {
        defval: "",
      });

      const result = await apiFetchWithToken("/api/imports/users/parse-xlsx-rows", token, {
        method: "POST",
        body: JSON.stringify({ rows }),
      });

      setUsersPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} user row(s) from Excel`);
    } catch (err: any) {
      setStatus(err.message || "Excel parse failed");
    }
  }

  async function createUsers() {
    try {
      const result = await apiFetchWithToken("/api/imports/users/bulk-create", token, {
        method: "POST",
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
      const result = await apiFetchWithToken("/api/imports/enrollment/parse", token, {
        method: "POST",
        body: JSON.stringify({ rows }),
      });
      setEnrollmentPreview(result.rows || []);
      setStatus(`Parsed ${result.parsed_count} enrollment row(s)`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment JSON parse failed");
    }
  }

  async function publishEnrollment() {
    try {
      const result = await apiFetchWithToken("/api/imports/enrollment/publish", token, {
        method: "POST",
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
      <p>Upload Excel/CSV to load users, then publish enrollment as JSON.</p>

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
        <h2>1. Load Users from Excel</h2>
        <p>
          Expected columns: <b>Reg No.</b>, <b>Names</b>, <b>Email Address</b>, <b>Session</b>
        </p>

        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleUsersExcelUpload(file);
          }}
        />

        <div style={{ marginTop: 16 }}>
          <h3>Or paste CSV</h3>
          <textarea
            value={usersCsv}
            onChange={(e) => setUsersCsv(e.target.value)}
            placeholder="Paste roster CSV here"
            style={{ width: "100%", minHeight: 180 }}
          />
          <div style={{ marginTop: 12 }}>
            <button onClick={parseUsersCsv}>Parse Users CSV</button>
          </div>
        </div>

        <div style={{ marginTop: 12 }}>
          <button onClick={createUsers} disabled={usersPreview.length === 0}>
            Create / Update Users
          </button>
        </div>

        {usersPreview.length > 0 && (
          <pre style={{ marginTop: 12, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(usersPreview, null, 2)}
          </pre>
        )}
      </div>

      <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>2. Enrollment JSON</h2>
        <textarea
          value={enrollmentJson}
          onChange={(e) => setEnrollmentJson(e.target.value)}
          style={{ width: "100%", minHeight: 180 }}
        />
        <div style={{ marginTop: 12 }}>
          <button onClick={parseEnrollmentJson}>Parse Enrollment JSON</button>
          <button
            onClick={publishEnrollment}
            disabled={enrollmentPreview.length === 0}
            style={{ marginLeft: 8 }}
          >
            Publish Enrollment
          </button>
        </div>

        {enrollmentPreview.length > 0 && (
          <pre style={{ marginTop: 12, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(enrollmentPreview, null, 2)}
          </pre>
        )}
      </div>

      <p>{status}</p>
    </main>
  );
}
