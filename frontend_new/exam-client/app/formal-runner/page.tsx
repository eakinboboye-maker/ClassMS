"use client";

import { useEffect, useMemo, useState } from "react";
import { apiFetch, login } from "../../lib/api";

type ExamQuestion = {
  question_id: number;
  type: string;
  prompt_md: string;
  marks: number;
  options?: { option_key: string; text: string }[];
  gaps?: { gap_key: string }[];
};

export default function FormalRunnerPage() {
  const [email, setEmail] = useState("student1@example.com");
  const [password, setPassword] = useState("student123");
  const [assessmentId, setAssessmentId] = useState("1");
  const [sebHash, setSebHash] = useState("demo-valid-config-key");
  const [token, setToken] = useState("");
  const [session, setSession] = useState<any>(null);
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [status, setStatus] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(0);

  async function startExam() {
    try {
      const auth = await login(email, password);
      setToken(auth.access_token);

      const started = await apiFetch(`/api/formal-exams/${assessmentId}/start`, auth.access_token, {
        method: "POST",
        headers: { "X-SafeExamBrowser-ConfigKeyHash": sebHash },
      });
      setSession(started);

      const paper = await apiFetch(`/api/formal-exams/${assessmentId}/paper`, auth.access_token);
      setQuestions(paper.items || []);
      setStatus("Exam loaded");

      if (started.expires_at) {
        const expireTs = new Date(started.expires_at).getTime();
        setSecondsLeft(Math.max(0, Math.floor((expireTs - Date.now()) / 1000)));
      }
    } catch (err: any) {
      setStatus(err.message || "Failed to start exam");
    }
  }

  useEffect(() => {
    if (!secondsLeft) return;
    const t = setInterval(() => setSecondsLeft((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [secondsLeft]);

  const progressPct = useMemo(() => {
    if (!questions.length) return 0;
    let answered = 0;
    for (const q of questions) {
      const a = answers[q.question_id];
      if (!a) continue;
      if (q.type === "mcq_single" && a.selected_option) answered++;
      else if (q.type === "mcq_multi" && (a.selected_options || []).length) answered++;
      else if (q.type === "fill_gap" && Object.values(a.gaps || {}).every(Boolean)) answered++;
    }
    return Math.round((answered / questions.length) * 100);
  }, [answers, questions]);

  async function autosave() {
    if (!session || !token) return;
    try {
      const payload = {
        responses: Object.entries(answers).map(([question_id, response]) => ({
          question_id: Number(question_id),
          response,
        })),
      };
      await apiFetch(`/api/formal-exams/attempts/${session.attempt_id}/autosave?exam_session_token=${encodeURIComponent(session.exam_session_token)}`, token, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setStatus("Autosaved");
    } catch (err: any) {
      setStatus(err.message || "Autosave failed");
    }
  }

  async function submit() {
    if (!session || !token) return;
    try {
      await apiFetch(`/api/formal-exams/attempts/${session.attempt_id}/submit`, token, {
        method: "POST",
        body: JSON.stringify({
          exam_session_token: session.exam_session_token,
          submitted_payload: { done: true, source: "next-formal-runner" },
        }),
      });
      setStatus("Submitted");
    } catch (err: any) {
      setStatus(err.message || "Submit failed");
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Formal Exam Runner</h1>
        <p className="muted">Sign in and start your exam session.</p>
      </div>

      {!session && (
        <div className="card">
          <div className="row">
            <div style={{ flex: 1, minWidth: 260 }}>
              <label>Email</label>
              <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
            </div>
            <div style={{ flex: 1, minWidth: 260 }}>
              <label>Password</label>
              <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
            </div>
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <div style={{ flex: 1, minWidth: 220 }}>
              <label>Assessment ID</label>
              <input value={assessmentId} onChange={(e) => setAssessmentId(e.target.value)} />
            </div>
            <div style={{ flex: 1, minWidth: 220 }}>
              <label>SEB Config Hash</label>
              <input value={sebHash} onChange={(e) => setSebHash(e.target.value)} />
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button onClick={startExam}>Start Exam</button>
          </div>
        </div>
      )}

      {session && (
        <>
          <div className="card">
            <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <strong>Attempt #{session.attempt_id}</strong>
                <div className="muted">Time left: {secondsLeft}s</div>
              </div>
              <div style={{ minWidth: 220 }}>
                <div className="muted">Progress {progressPct}%</div>
                <div className="progress"><div style={{ width: `${progressPct}%` }} /></div>
              </div>
            </div>
          </div>

          {questions.map((q) => (
            <div className="question" key={q.question_id}>
              <p><strong>Q{q.question_id}.</strong> {q.prompt_md}</p>

              {q.type === "mcq_single" && (
                <div className="row">
                  {(q.options || []).map((opt) => (
                    <label key={opt.option_key} style={{ width: "100%" }}>
                      <input
                        type="radio"
                        name={`q-${q.question_id}`}
                        checked={answers[q.question_id]?.selected_option === opt.option_key}
                        onChange={() =>
                          setAnswers((prev) => ({
                            ...prev,
                            [q.question_id]: { selected_option: opt.option_key },
                          }))
                        }
                      />{" "}
                      {opt.option_key}. {opt.text}
                    </label>
                  ))}
                </div>
              )}

              {q.type === "mcq_multi" && (
                <div className="row">
                  {(q.options || []).map((opt) => {
                    const selected = answers[q.question_id]?.selected_options || [];
                    return (
                      <label key={opt.option_key} style={{ width: "100%" }}>
                        <input
                          type="checkbox"
                          checked={selected.includes(opt.option_key)}
                          onChange={(e) => {
                            const next = e.target.checked
                              ? [...selected, opt.option_key]
                              : selected.filter((x: string) => x !== opt.option_key);
                            setAnswers((prev) => ({
                              ...prev,
                              [q.question_id]: { selected_options: next },
                            }));
                          }}
                        />{" "}
                        {opt.option_key}. {opt.text}
                      </label>
                    );
                  })}
                </div>
              )}

              {q.type === "fill_gap" && (
                <div className="row">
                  {(q.gaps || []).map((gap) => (
                    <div key={gap.gap_key} style={{ flex: 1, minWidth: 220 }}>
                      <label>{gap.gap_key}</label>
                      <input
                        value={answers[q.question_id]?.gaps?.[gap.gap_key] || ""}
                        onChange={(e) =>
                          setAnswers((prev) => ({
                            ...prev,
                            [q.question_id]: {
                              gaps: {
                                ...(prev[q.question_id]?.gaps || {}),
                                [gap.gap_key]: e.target.value,
                              },
                            },
                          }))
                        }
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          <div className="card">
            <div className="row">
              <button onClick={autosave}>Autosave</button>
              <button onClick={submit}>Submit</button>
            </div>
          </div>
        </>
      )}

      <p>{status}</p>
    </main>
  );
}
