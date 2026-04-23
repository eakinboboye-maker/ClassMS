"use client";

import { useEffect, useState } from "react";
import { BackendClient } from "../../lib/backendClient";

const api = new BackendClient({ baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000" });

type ExamQuestion = {
  question_id: number;
  type: string;
  prompt_md: string;
  marks: number;
};

export default function FormalRunnerPage() {
  const [email, setEmail] = useState("student1@example.com");
  const [password, setPassword] = useState("student123");
  const [assessmentId, setAssessmentId] = useState("1");
  const [sebHash, setSebHash] = useState("demo-valid-config-key");
  const [session, setSession] = useState<any>(null);
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [status, setStatus] = useState("");
  const [nonce, setNonce] = useState<string | undefined>(undefined);

  async function startExam() {
    try {
      const auth = await api.login(email, password);
      api.setToken(auth.access_token);

      const started = await api.startFormalExam(Number(assessmentId), sebHash);
      setSession(started);

      const paperRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/formal-exams/${assessmentId}/paper`, {
        headers: { Authorization: `Bearer ${auth.access_token}` },
      });
      if (!paperRes.ok) throw new Error(`Paper fetch failed: ${paperRes.status}`);
      const paper = await paperRes.json();
      setQuestions(paper.items);
      setStatus("Exam loaded");
    } catch (err: any) {
      setStatus(err.message || "Failed to start exam");
    }
  }

  useEffect(() => {
    if (!session) return;
    const timer = setInterval(async () => {
      try {
        const hb = await api.formalHeartbeat(session.attempt_id, session.exam_session_token, nonce);
        setNonce(hb.next_nonce);
      } catch (err) {
        console.error(err);
      }
    }, 15000);

    return () => clearInterval(timer);
  }, [session, nonce]);

  async function autosave() {
    if (!session) return;
    try {
      const payload = {
        responses: Object.entries(answers).map(([qid, response]) => ({
          question_id: Number(qid),
          response,
        })),
      };

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/formal-exams/attempts/${session.attempt_id}/autosave?exam_session_token=${encodeURIComponent(session.exam_session_token)}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${api.token}`,
          },
          body: JSON.stringify(payload),
        }
      );
      if (!res.ok) throw new Error(`Autosave failed: ${res.status}`);
      setStatus("Autosaved");
    } catch (err: any) {
      setStatus(err.message || "Autosave failed");
    }
  }

  async function submit() {
    if (!session) return;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/formal-exams/attempts/${session.attempt_id}/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${api.token}`,
        },
        body: JSON.stringify({
          exam_session_token: session.exam_session_token,
          submitted_payload: { done: true, source: "next-formal-runner" },
        }),
      });
      if (!res.ok) throw new Error(`Submit failed: ${res.status}`);
      setStatus("Submitted");
    } catch (err: any) {
      setStatus(err.message || "Submit failed");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Formal Exam Runner</h1>

      {!session && (
        <div style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <br /><br />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
          <br /><br />
          <input value={assessmentId} onChange={(e) => setAssessmentId(e.target.value)} placeholder="Assessment ID" />
          <br /><br />
          <input value={sebHash} onChange={(e) => setSebHash(e.target.value)} placeholder="SEB Config Hash" />
          <br /><br />
          <button onClick={startExam}>Start Exam</button>
        </div>
      )}

      {questions.map((q) => (
        <div key={q.question_id} style={{ background: "#fff", padding: 16, borderRadius: 12, marginBottom: 16 }}>
          <p><strong>Q{q.question_id}.</strong> {q.prompt_md}</p>

          {q.type === "mcq_single" && (
            <input
              placeholder="Selected option key e.g. a"
              value={answers[q.question_id]?.selected_option || ""}
              onChange={(e) =>
                setAnswers((prev) => ({
                  ...prev,
                  [q.question_id]: { selected_option: e.target.value },
                }))
              }
            />
          )}

          {q.type === "mcq_multi" && (
            <input
              placeholder="Selected options comma-separated e.g. a,c"
              value={(answers[q.question_id]?.selected_options || []).join(",")}
              onChange={(e) =>
                setAnswers((prev) => ({
                  ...prev,
                  [q.question_id]: {
                    selected_options: e.target.value
                      .split(",")
                      .map((x) => x.trim())
                      .filter(Boolean),
                  },
                }))
              }
            />
          )}

          {q.type === "fill_gap" && (
            <textarea
              placeholder='JSON gaps e.g. {"GAP1":"created","GAP2":"destroyed"}'
              value={JSON.stringify(answers[q.question_id]?.gaps || {})}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setAnswers((prev) => ({
                    ...prev,
                    [q.question_id]: { gaps: parsed },
                  }));
                } catch {
                  // ignore bad JSON while typing
                }
              }}
            />
          )}
        </div>
      ))}

      {session && (
        <div>
          <button onClick={autosave}>Autosave</button>
          <button onClick={submit} style={{ marginLeft: 8 }}>Submit</button>
        </div>
      )}

      <p>{status}</p>
    </main>
  );
}
