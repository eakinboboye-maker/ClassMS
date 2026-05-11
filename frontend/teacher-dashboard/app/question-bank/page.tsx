"use client";

import { useState } from "react";
import { apiFetch } from "../../lib/imports-api";

export default function QuestionBankPage() {
  const [token, setToken] = useState("");
  const [text, setText] = useState("");
  const [mode, setMode] = useState<"text" | "csv">("text");
  const [preview, setPreview] = useState<any[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [status, setStatus] = useState("");

  async function parseQuestions() {
    try {
      const path = mode === "text" ? "/api/imports/questions/parse-text" : "/api/imports/questions/parse-csv";
      const result = await apiFetch(path, token, {
        method: "POST",
        body: JSON.stringify({ text }),
      });
      setPreview(result.items || []);
      setWarnings(result.warnings || []);
      setStatus(`Parsed ${result.count} question(s)`);
    } catch (err: any) {
      setStatus(err.message || "Parse failed");
    }
  }

  async function publishQuestions() {
    try {
      const result = await apiFetch("/api/imports/questions/publish", token, {
        method: "POST",
        body: JSON.stringify({ items: preview }),
      });
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
        <h2 className="card-title">Teacher Access</h2>
        <label className="label">Teacher access token</label>
        <input className="input" value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste teacher JWT" />
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
        {status ? <div className="notice notice-info">{status}</div> : null}
      </section>

      {warnings.length > 0 && (
        <section className="card">
          <h2 className="card-title">Warnings</h2>
          <ul className="list">{warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>
        </section>
      )}

      {preview.length > 0 && (
        <section className="card">
          <h2 className="card-title">Preview</h2>
          {preview.map((item, i) => (
            <div key={i} className="preview-item">
              <div className="kv"><strong>Type:</strong> {item.type}</div>
              <div className="kv"><strong>Prompt:</strong> {item.prompt_md}</div>
              <div className="kv"><strong>Topics:</strong> {(item.topics || []).join(", ")}</div>
              <div className="kv"><strong>Labels:</strong> {(item.labels || []).join(", ")}</div>
              <div className="kv"><strong>Explanation visible after submit:</strong> {String(item.show_explanation_after_submit)}</div>
              {(item.options || []).length > 0 && (
                <ul className="list">
                  {item.options.map((opt: any, j: number) => (
                    <li key={j}>{opt.option_key}. {opt.text} {opt.is_correct ? "✅" : ""}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}
    </main>
  );
}
