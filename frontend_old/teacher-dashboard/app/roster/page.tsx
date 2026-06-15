"use client";

import { useMemo, useState } from "react";
import * as XLSX from "xlsx";
import { apiFetch } from "../../lib/imports-api";

type RawRow = Record<string, unknown>;

type ParsedUserRow = {
  matric_no: string;
  full_name: string;
  email: string;
  session: string;
  role: "student";
};

type ParsedEnrollmentRow = {
  reg_no: string;
  course_code: string;
  section: string;
  session: string;
};

type UserColumnKey = "regNo" | "names" | "email" | "session";
type EnrollmentColumnKey = "regNo" | "courseCode" | "section" | "session";

const USER_COLUMNS: Array<{ key: UserColumnKey; label: string }> = [
  { key: "regNo", label: "Reg No." },
  { key: "names", label: "Names" },
  { key: "email", label: "Email Address" },
  { key: "session", label: "Session" },
];

const ENROLLMENT_COLUMNS: Array<{ key: EnrollmentColumnKey; label: string }> = [
  { key: "regNo", label: "Reg No." },
  { key: "courseCode", label: "Course Code" },
  { key: "section", label: "Section" },
  { key: "session", label: "Session" },
];

function normalizeCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  return String(value).trim();
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export default function RosterPage() {
  const [mode, setMode] = useState<"users" | "enrollment">("users");
  const [rawRows, setRawRows] = useState<RawRow[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [fileName, setFileName] = useState("");
  const [status, setStatus] = useState("Upload an Excel file to begin.");
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [defaultPassword, setDefaultPassword] = useState("changeme123");

  const [userMapping, setUserMapping] = useState<Record<UserColumnKey, string>>({
    regNo: "",
    names: "",
    email: "",
    session: "",
  });

  const [enrollmentMapping, setEnrollmentMapping] = useState<Record<EnrollmentColumnKey, string>>({
    regNo: "",
    courseCode: "",
    section: "",
    session: "",
  });

  const [userPreview, setUserPreview] = useState<ParsedUserRow[]>([]);
  const [enrollmentPreview, setEnrollmentPreview] = useState<ParsedEnrollmentRow[]>([]);

  async function handleExcelFile(file: File) {
    try {
      setStatus("Reading Excel file...");
      setFileName(file.name);
      setValidationErrors([]);
      setUserPreview([]);
      setEnrollmentPreview([]);

      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: "array" });
      const firstSheetName = workbook.SheetNames[0];
      if (!firstSheetName) throw new Error("No sheet found in workbook");

      const sheet = workbook.Sheets[firstSheetName];
      const rows = XLSX.utils.sheet_to_json<RawRow>(sheet, { defval: "" });
      if (!rows.length) throw new Error("No data rows found in the first sheet");

      setHeaders(Object.keys(rows[0] || {}));
      setRawRows(rows);
      setStatus(`Loaded ${rows.length} row(s) from ${file.name}`);
    } catch (err: any) {
      setStatus(err.message || "Failed to read Excel file");
      setHeaders([]);
      setRawRows([]);
    }
  }

  const canBuildUserPreview = useMemo(
    () => rawRows.length > 0 && USER_COLUMNS.every((c) => userMapping[c.key]),
    [rawRows, userMapping]
  );

  const canBuildEnrollmentPreview = useMemo(
    () => rawRows.length > 0 && ENROLLMENT_COLUMNS.every((c) => enrollmentMapping[c.key]),
    [rawRows, enrollmentMapping]
  );

  function buildUserPreview() {
    const rows: ParsedUserRow[] = rawRows.map((row) => ({
      matric_no: normalizeCell(row[userMapping.regNo]),
      full_name: normalizeCell(row[userMapping.names]),
      email: normalizeCell(row[userMapping.email]),
      session: normalizeCell(row[userMapping.session]),
      role: "student",
    }));

    const errors: string[] = [];
    const seenEmails = new Set<string>();
    const seenMatric = new Set<string>();

    rows.forEach((row, index) => {
      const rowNo = index + 2;
      if (!row.matric_no) errors.push(`Row ${rowNo}: missing Reg No.`);
      if (!row.full_name) errors.push(`Row ${rowNo}: missing Names`);
      if (!row.email) errors.push(`Row ${rowNo}: missing Email Address`);
      if (row.email && !validateEmail(row.email)) errors.push(`Row ${rowNo}: invalid email (${row.email})`);
      if (!row.session) errors.push(`Row ${rowNo}: missing Session`);

      if (row.email) {
        const emailKey = row.email.toLowerCase();
        if (seenEmails.has(emailKey)) errors.push(`Row ${rowNo}: duplicate email (${row.email})`);
        seenEmails.add(emailKey);
      }

      if (row.matric_no) {
        const matricKey = row.matric_no.toLowerCase();
        if (seenMatric.has(matricKey)) errors.push(`Row ${rowNo}: duplicate Reg No. (${row.matric_no})`);
        seenMatric.add(matricKey);
      }
    });

    const filtered = rows.filter((row) => row.matric_no || row.full_name || row.email || row.session);
    setUserPreview(filtered);
    setValidationErrors(errors);
    setStatus(`Prepared ${filtered.length} user row(s)`);
  }

  function buildEnrollmentPreview() {
    const rows: ParsedEnrollmentRow[] = rawRows.map((row) => ({
      reg_no: normalizeCell(row[enrollmentMapping.regNo]),
      course_code: normalizeCell(row[enrollmentMapping.courseCode]),
      section: normalizeCell(row[enrollmentMapping.section]),
      session: normalizeCell(row[enrollmentMapping.session]),
    }));

    const errors: string[] = [];
    rows.forEach((row, index) => {
      const rowNo = index + 2;
      if (!row.reg_no) errors.push(`Row ${rowNo}: missing Reg No.`);
      if (!row.course_code) errors.push(`Row ${rowNo}: missing Course Code`);
      if (!row.section) errors.push(`Row ${rowNo}: missing Section`);
      if (!row.session) errors.push(`Row ${rowNo}: missing Session`);
    });

    const filtered = rows.filter((row) => row.reg_no || row.course_code || row.section || row.session);
    setEnrollmentPreview(filtered);
    setValidationErrors(errors);
    setStatus(`Prepared ${filtered.length} enrollment row(s)`);
  }

  async function validateUsersOnBackend() {
    try {
      if (!userPreview.length) throw new Error("No user preview rows available");

      const backendRows = userPreview.map((row) => ({
        "Reg No.": row.matric_no,
        "Names": row.full_name,
        "Email Address": row.email,
        "Session": row.session,
      }));

      const result = await apiFetch("/api/imports/users/parse-xlsx-rows", {
        method: "POST",
        body: JSON.stringify({ rows: backendRows }),
      });

      setStatus(`Backend validated ${result.parsed_count} user row(s)`);
    } catch (err: any) {
      setStatus(err.message || "Backend validation failed");
    }
  }

  async function createUsers() {
    try {
      if (!userPreview.length) throw new Error("No user preview rows available");

      const result = await apiFetch("/api/imports/users/bulk-create", {
        method: "POST",
        body: JSON.stringify({
          users: userPreview.map((row) => ({
            email: row.email,
            full_name: row.full_name,
            matric_no: row.matric_no,
            role: row.role,
          })),
          default_password: defaultPassword,
          skip_existing: true,
        }),
      });

      setStatus(`Created ${result.created_count} user(s), skipped ${result.skipped_count}`);
    } catch (err: any) {
      setStatus(err.message || "User creation failed");
    }
  }

  async function validateEnrollmentOnBackend() {
    try {
      if (!enrollmentPreview.length) throw new Error("No enrollment preview rows available");

      const backendRows = enrollmentPreview.map((row) => ({
        "Reg No.": row.reg_no,
        "Course Code": row.course_code,
        "Section": row.section,
        "Session": row.session,
      }));

      const result = await apiFetch("/api/imports/enrollment/parse", {
        method: "POST",
        body: JSON.stringify({ rows: backendRows }),
      });

      setStatus(`Backend validated ${result.parsed_count} enrollment row(s)`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment validation failed");
    }
  }

  async function publishEnrollment() {
    try {
      if (!enrollmentPreview.length) throw new Error("No enrollment preview rows available");

      const result = await apiFetch("/api/imports/enrollment/publish", {
        method: "POST",
        body: JSON.stringify({ rows: enrollmentPreview }),
      });

      setStatus(`Enrolled ${result.enrolled_count}, skipped ${result.skipped_count}`);
    } catch (err: any) {
      setStatus(err.message || "Enrollment publish failed");
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <h1>Roster Import</h1>
      <p>Upload an Excel file, map the needed columns in any order, preview the rows, then create users or publish enrollment.</p>

      <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
        <h2>1. Upload Excel File</h2>
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleExcelFile(file);
          }}
        />
        {fileName ? <p>Loaded file: {fileName}</p> : null}

        <div style={{ marginTop: 12 }}>
          <button onClick={() => setMode("users")} disabled={mode === "users"}>
            Users Import
          </button>
          <button onClick={() => setMode("enrollment")} disabled={mode === "enrollment"} style={{ marginLeft: 8 }}>
            Enrollment Import
          </button>
        </div>
      </section>

      {headers.length > 0 && mode === "users" && (
        <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <h2>2. Map User Columns</h2>
          <p>Pick the columns for user creation. Column order does not matter.</p>

          <div style={{ display: "grid", gap: 12 }}>
            {USER_COLUMNS.map((item) => (
              <label key={item.key} style={{ display: "grid", gap: 6 }}>
                <span>{item.label}</span>
                <select
                  value={userMapping[item.key]}
                  onChange={(e) => setUserMapping((prev) => ({ ...prev, [item.key]: e.target.value }))}
                >
                  <option value="">Select a column</option>
                  {headers.map((header) => (
                    <option key={header} value={header}>{header}</option>
                  ))}
                </select>
              </label>
            ))}
          </div>

          <div style={{ marginTop: 12 }}>
            <button onClick={buildUserPreview} disabled={!canBuildUserPreview}>Build User Preview</button>
          </div>
        </section>
      )}

      {headers.length > 0 && mode === "enrollment" && (
        <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <h2>2. Map Enrollment Columns</h2>
          <p>Pick the columns for enrollment publishing. Column order does not matter.</p>

          <div style={{ display: "grid", gap: 12 }}>
            {ENROLLMENT_COLUMNS.map((item) => (
              <label key={item.key} style={{ display: "grid", gap: 6 }}>
                <span>{item.label}</span>
                <select
                  value={enrollmentMapping[item.key]}
                  onChange={(e) => setEnrollmentMapping((prev) => ({ ...prev, [item.key]: e.target.value }))}
                >
                  <option value="">Select a column</option>
                  {headers.map((header) => (
                    <option key={header} value={header}>{header}</option>
                  ))}
                </select>
              </label>
            ))}
          </div>

          <div style={{ marginTop: 12 }}>
            <button onClick={buildEnrollmentPreview} disabled={!canBuildEnrollmentPreview}>Build Enrollment Preview</button>
          </div>
        </section>
      )}

      {validationErrors.length > 0 && (
        <section style={{ background: "#fff7ed", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <h2>Validation Warnings</h2>
          <ul>
            {validationErrors.map((err, i) => <li key={i}>{err}</li>)}
          </ul>
        </section>
      )}

      {mode === "users" && userPreview.length > 0 && (
        <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <h2>3. User Preview</h2>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", marginBottom: 6 }}>Default Password</label>
            <input
              value={defaultPassword}
              onChange={(e) => setDefaultPassword(e.target.value)}
              placeholder="Default password"
              style={{ width: 260 }}
            />
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Reg No.</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Names</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Email</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Session</th>
                </tr>
              </thead>
              <tbody>
                {userPreview.slice(0, 50).map((row, i) => (
                  <tr key={i}>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.matric_no}</td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.full_name}</td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.email}</td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.session}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
            <button onClick={validateUsersOnBackend}>Validate on Backend</button>
            <button onClick={createUsers}>Create / Update Users</button>
          </div>
        </section>
      )}

      {mode === "enrollment" && enrollmentPreview.length > 0 && (
        <section style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <h2>3. Enrollment Preview</h2>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Reg No.</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Course Code</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Section</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>Session</th>
                </tr>
              </thead>
              <tbody>
                {enrollmentPreview.slice(0, 50).map((row, i) => (
                  <tr key={i}>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.reg_no}</td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.course_code}</td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.section}</td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{row.session}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
            <button onClick={validateEnrollmentOnBackend}>Validate Enrollment</button>
            <button onClick={publishEnrollment}>Publish Enrollment</button>
          </div>
        </section>
      )}

      <p>{status}</p>
    </main>
  );
}
