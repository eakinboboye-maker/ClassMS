"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/imports-api";
import { loadTeacherSession } from "../../lib/auth";

export default function QuestionBankPage() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState<"text" | "csv">("text");
  const [preview, setPreview] = useState<any[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const session = loadTeacherSession();
    if (!session?.token) setStatus("No teacher session found. Please sign in on the Home page.");
  }, []);

  async function parseQuestions() {
    try {
      const path = mode === "text" ? "/api/imports/questions/parse-text" : "/api/imports/questions/parse-csv";
      const result = await apiFetch(path, { method: "POST", body: JSON.stringify({ text }) });
      setPreview(result.items || []);
      setWarnings(result.warnings || []);
      setStatus(`Parsed ${result.count} question(s)`);
    } catch (err: any) {
      setStatus(err.message || "Parse failed");
    }
  }

  async function publishQuestions() {
    try {
      const result = await apiFetch("/api/imports/questions/publish", { method: "POST", body: JSON.stringify({ items: preview }) });
      setStatus(`Published ${result.created_count} question(s)`);
    } catch (err: any) {
      setStatus(err.message || "Publish failed");
    }
  }

  return (
    <main>
      <h1 className="page-title">Question Bank Upload</h1>
      <p className="page-subtitle">Parse raw question content, preview the result, and publish to the bank.</p>
      <section className="card card-accent">
        <h2 className="card-title">Teacher Session</h2>
        <div className="notice notice-info">{status || "Signed-in teacher session will be used automatically."}</div>
      </section>
      <section className="card">
        <h2 className="card-title">Question Source</h2>
        <div className="button-row">
          <button className={`btn ${mode === "text" ? "btn-primary" : "btn-secondary"}`} onClick={() => setMode("text")}>Parser Text</button>
          <button className={`btn ${mode === "csv" ? "btn-primary" : "btn-secondary"}`} onClick={() => setMode("csv")}>Mixed CSV</button>
        </div>
        <div className="spacer-16" />
        <label className="label">{mode === "text" ? "Paste parser-style question text" : "Paste mixed question bank CSV"}</label>
        <textarea className="textarea" value={text} onChange={(e) => setText(e.target.value)} placeholder={mode === "text" ? "Paste question_template.txt content here" : "Paste mixed_question_bank_template.csv content here"} />
        <div className="button-row">
          <button className="btn btn-primary" onClick={parseQuestions}>Parse</button>
          <button className="btn btn-success" onClick={publishQuestions} disabled={preview.length === 0}>Publish Parsed Questions</button>
        </div>
      </section>
      {warnings.length > 0 && <section className="card"><h2 className="card-title">Warnings</h2><ul className="list">{warnings.map((w, i) => <li key={i}>{w}</li>)}</ul></section>}
      {preview.length > 0 && <section className="card"><h2 className="card-title">Preview</h2>{preview.map((item, i) => <div key={i} className="preview-item"><div className="kv"><strong>Type:</strong> {item.type}</div><div className="kv"><strong>Prompt:</strong> {item.prompt_md}</div></div>)}</section>}
    </main>
  );
}
