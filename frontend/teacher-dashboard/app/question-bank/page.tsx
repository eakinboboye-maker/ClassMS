"use client";

import { useState } from "react";

export default function QuestionBankPage() {
  const [token, setToken] = useState("");
  const [text, setText] = useState("");
  const [mode, setMode] = useState<"text" | "csv">("text");
  const [status, setStatus] = useState("Paste question content, then parse and publish.");
  const [preview] = useState([
    {
      type: "mcq_single",
      prompt_md: "Which of the following best describes digital abstraction?",
      topics: ["digital abstraction", "binary"],
      labels: ["week1", "lesson", "easy"],
      show_explanation_after_submit: true,
      options: [
        { option_key: "a", text: "Representation using continuous values only", is_correct: false },
        { option_key: "b", text: "Representation using discrete values", is_correct: true },
      ],
    },
  ]);

  return (
    <main>
      <h1 className="page-title">Question Bank Upload</h1>
      <p className="page-subtitle">Parse raw question content, preview the result, and publish to the bank.</p>

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
        <h2 className="card-title">Question Source</h2>
        <div className="button-row">
          <button className={`btn ${mode === "text" ? "btn-primary" : "btn-secondary"}`} onClick={() => setMode("text")}>Parser Text</button>
          <button className={`btn ${mode === "csv" ? "btn-primary" : "btn-secondary"}`} onClick={() => setMode("csv")}>Mixed CSV</button>
        </div>

        <div className="spacer-16" />
        <label className="label">{mode === "text" ? "Paste parser-style question text" : "Paste mixed question bank CSV"}</label>
        <textarea
          className="textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={mode === "text" ? "Paste question_template.txt content here" : "Paste mixed_question_bank_template.csv content here"}
        />

        <div className="button-row">
          <button className="btn btn-primary" onClick={() => setStatus("Parsed preview successfully.")}>Parse</button>
          <button className="btn btn-success" onClick={() => setStatus("Published parsed questions.")}>Publish Parsed Questions</button>
        </div>

        <div className="notice notice-info">{status}</div>
      </section>

      <section className="card">
        <h2 className="card-title">Preview</h2>
        {preview.map((item, i) => (
          <div key={i} className="preview-item">
            <div className="kv"><strong>Type:</strong> {item.type}</div>
            <div className="kv"><strong>Prompt:</strong> {item.prompt_md}</div>
            <div className="kv"><strong>Topics:</strong> {item.topics.join(", ")}</div>
            <div className="kv"><strong>Labels:</strong> {item.labels.join(", ")}</div>
            <div className="kv"><strong>Explanation visible after submit:</strong> {String(item.show_explanation_after_submit)}</div>
            <ul className="list">
              {item.options.map((opt, j) => (
                <li key={j}>
                  {opt.option_key}. {opt.text} {opt.is_correct ? "✅" : ""}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </main>
  );
}
