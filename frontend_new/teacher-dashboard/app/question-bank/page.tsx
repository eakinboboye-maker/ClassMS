"use client";

import { useState } from "react";
import { apiFetch } from "../../lib/api";

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
      <div className="card">
        <h1>Question Bank Upload</h1>
        <p className="muted">Paste parser text or mixed CSV, preview, then publish.</p>
      </div>

      <div className="card">
        <label>Teacher access token</label>
        <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Paste teacher JWT" style={{ marginTop: 8 }} />
      </div>

      <div className="card">
        <div className="row" style={{ marginBottom: 12 }}>
          <button onClick={() => setMode("text")} disabled={mode === "text"}>Parser Text</button>
          <button onClick={() => setMode("csv")} disabled={mode === "csv"}>Mixed CSV</button>
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={mode === "text" ? "Paste question_template.txt content here" : "Paste mixed_question_bank_template.csv content here"}
          style={{ minHeight: 260 }}
        />

        <div className="row" style={{ marginTop: 12 }}>
          <button onClick={parseQuestions}>Parse</button>
          <button onClick={publishQuestions} disabled={preview.length === 0}>Publish Parsed Questions</button>
        </div>
      </div>

      {warnings.length > 0 && (
        <div className="card">
          <h3>Warnings</h3>
          <ul>{warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>
        </div>
      )}

      {preview.length > 0 && (
        <div className="card">
          <h2>Preview</h2>
          {preview.map((item, i) => (
            <div key={i} className="card">
              <div><b>Type:</b> {item.type}</div>
              <div><b>Prompt:</b> {item.prompt_md}</div>
              <div><b>Topics:</b> {(item.topics || []).join(", ")}</div>
              <div><b>Labels:</b> {(item.labels || []).join(", ")}</div>
              <div><b>Explanation visible after submit:</b> {String(item.show_explanation_after_submit)}</div>
              {(item.options || []).length > 0 && (
                <ul>
                  {item.options.map((opt: any, j: number) => (
                    <li key={j}>{opt.option_key}. {opt.text} {opt.is_correct ? "✅" : ""}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      <p>{status}</p>
    </main>
  );
}
