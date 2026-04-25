"use client";

import { useEffect, useMemo, useState } from "react";
import { BackendClient } from "../lib/api";

const api = new BackendClient();

type ExamQuestion = { question_id: number; type: string; prompt_md: string; marks: number };

export default function FormalExamRunner() {
  const [email, setEmail] = useState("student1@example.com");
  const [password, setPassword] = useState("student123");
  const [assessmentId, setAssessmentId] = useState("1");
  const [sebHash, setSebHash] = useState("demo-valid-config-key");
  const [session, setSession] = useState<any>(null);
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [status, setStatus] = useState("Ready");
  const [nonce, setNonce] = useState<string | undefined>(undefined);
  const [timeLeft, setTimeLeft] = useState<string>("—");

  const answeredCount = useMemo(() => Object.keys(answers).length, [answers]);
  const progress = questions.length ? Math.round((answeredCount / questions.length) * 100) : 0;

  useEffect(() => {
    if (!session?.expires_at) return;
    const timer = setInterval(() => {
      const ms = new Date(session.expires_at).getTime() - Date.now();
      const total = Math.max(ms, 0);
      const mins = Math.floor(total / 60000);
      const secs = Math.floor((total % 60000) / 1000);
      setTimeLeft(`${mins}:${String(secs).padStart(2, "0")}`);
    }, 1000);
    return () => clearInterval(timer);
  }, [session]);

  useEffect(() => {
    if (!session) return;
    const timer = setInterval(async () => {
      try {
        const hb = await api.formalHeartbeat(session.attempt_id, session.exam_session_token, nonce);
        setNonce(hb.next_nonce);
      } catch (err: any) {
        setStatus(err.message || "Heartbeat failed");
      }
    }, 15000);
    return () => clearInterval(timer);
  }, [session, nonce]);

  async function startExam() {
    try {
      const auth = await api.login(email, password);
      api.setToken(auth.access_token);
      const started = await api.startFormalExam(Number(assessmentId), sebHash);
      setSession(started);
      const paper = await api.fetchPaper(Number(assessmentId));
      setQuestions(paper.items || []);
      setStatus("Exam started and paper loaded.");
    } catch (err: any) {
      setStatus(err.message || "Failed to start exam");
    }
  }

  async function autosave() {
    if (!session) return;
    try {
      const responses = Object.entries(answers).map(([question_id, response]) => ({ question_id: Number(question_id), response }));
      await api.autosave(session.attempt_id, session.exam_session_token, responses);
      setStatus(`Autosaved ${responses.length} response(s).`);
    } catch (err: any) {
      setStatus(err.message || "Autosave failed");
    }
  }

  async function submit() {
    if (!session) return;
    try {
      await api.submit(session.attempt_id, session.exam_session_token, { done: true, source: "vercel-formal-runner" });
      setStatus("Exam submitted successfully.");
    } catch (err: any) {
      setStatus(err.message || "Submit failed");
    }
  }

  return (
    <div className="exam-shell">
      <div className="hero">
        <div>
          <h1 className="title">Formal Exam Client</h1>
          <div className="subtitle">Polished Vercel-ready runner for objective and fill-gap exam flows.</div>
        </div>
        <div className="badge">Time left: <span className="mono" style={{ marginLeft: 8 }}>{timeLeft}</span></div>
      </div>

      {!session && (
        <div className="card">
          <div className="row">
            <div className="field"><label className="label">Email</label><input className="input" value={email} onChange={(e)=>setEmail(e.target.value)} /></div>
            <div className="field"><label className="label">Password</label><input className="input" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} /></div>
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <div className="field"><label className="label">Assessment ID</label><input className="input" value={assessmentId} onChange={(e)=>setAssessmentId(e.target.value)} /></div>
            <div className="field"><label className="label">SEB Config Hash</label><input className="input" value={sebHash} onChange={(e)=>setSebHash(e.target.value)} /></div>
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="btn" onClick={startExam}>Login and start exam</button>
          </div>
        </div>
      )}

      {session && (
        <div className="stickybar card">
          <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div className="badge">Attempt #{session.attempt_id}</div>
              <div className="subtitle" style={{ marginTop: 8 }}>Answered {answeredCount} of {questions.length} questions</div>
            </div>
            <div className="row">
              <button className="btn secondary" onClick={autosave}>Autosave</button>
              <button className="btn success" onClick={submit}>Submit exam</button>
            </div>
          </div>
          <div className="progress" style={{ marginTop: 12 }}><div style={{ width: `${progress}%` }} /></div>
        </div>
      )}

      {questions.map((q) => (
        <div key={q.question_id} className="card question-card">
          <h3>Question {q.question_id}</h3>
          <div className="subtitle">Type: {q.type} · Marks: {q.marks}</div>
          <p style={{ lineHeight: 1.6 }}>{q.prompt_md}</p>

          {q.type === "mcq_single" && (
            <input className="input" placeholder="Selected option key e.g. a" value={answers[q.question_id]?.selected_option || ""} onChange={(e) => setAnswers((prev) => ({ ...prev, [q.question_id]: { selected_option: e.target.value } }))} />
          )}

          {q.type === "mcq_multi" && (
            <input className="input" placeholder="Selected option keys e.g. a,c" value={(answers[q.question_id]?.selected_options || []).join(",")} onChange={(e) => setAnswers((prev) => ({ ...prev, [q.question_id]: { selected_options: e.target.value.split(",").map((x) => x.trim()).filter(Boolean) } }))} />
          )}

          {q.type === "fill_gap" && (
            <textarea className="textarea" placeholder='JSON object e.g. {"GAP1":"created","GAP2":"destroyed"}' value={JSON.stringify(answers[q.question_id]?.gaps || {})} onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value || "{}");
                setAnswers((prev) => ({ ...prev, [q.question_id]: { gaps: parsed } }));
              } catch {}
            }} />
          )}
        </div>
      ))}

      <p className="subtitle" style={{ marginTop: 18 }}>{status}</p>
    </div>
  );
}
