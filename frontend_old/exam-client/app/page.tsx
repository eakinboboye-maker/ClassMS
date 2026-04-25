"use client";

import { useState } from "react";
import { BackendClient } from "../lib/backendClient";

const api = new BackendClient({ baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000" });

export default function FormalExamHome() {
  const [email, setEmail] = useState("student1@example.com");
  const [password, setPassword] = useState("student123");
  const [assessmentId, setAssessmentId] = useState("1");
  const [sebHash, setSebHash] = useState("demo-valid-config-key");
  const [session, setSession] = useState<any>(null);
  const [status, setStatus] = useState("");
  const [nonce, setNonce] = useState<string | undefined>(undefined);

  async function loginAndStart() {
    try {
      const auth = await api.login(email, password);
      api.setToken(auth.access_token);
      const started = await api.startFormalExam(Number(assessmentId), sebHash);
      setSession(started);
      setStatus("Formal exam started");
    } catch (err: any) {
      setStatus(err.message || "Failed to start exam");
    }
  }

  async function heartbeat() {
    try {
      if (!session) return;
      const result = await api.formalHeartbeat(
        session.attempt_id,
        session.exam_session_token,
        nonce
      );
      setNonce(result.next_nonce);
      setStatus(`Heartbeat ok at ${result.last_seen_at}`);
    } catch (err: any) {
      setStatus(err.message || "Heartbeat failed");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Formal Exam Client</h1>

      <section style={{ background: "#fff", padding: 16, borderRadius: 12 }}>
        <div>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        </div>
        <br />
        <div>
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            type="password"
          />
        </div>
        <br />
        <div>
          <input
            value={assessmentId}
            onChange={(e) => setAssessmentId(e.target.value)}
            placeholder="Assessment ID"
          />
        </div>
        <br />
        <div>
          <input
            value={sebHash}
            onChange={(e) => setSebHash(e.target.value)}
            placeholder="SEB Config Hash"
          />
        </div>
        <br />
        <button onClick={loginAndStart}>Login and Start Formal Exam</button>
        <button onClick={heartbeat} disabled={!session} style={{ marginLeft: 8 }}>
          Heartbeat
        </button>
      </section>

      <pre style={{ whiteSpace: "pre-wrap", marginTop: 16 }}>{JSON.stringify(session, null, 2)}</pre>
      <p>{status}</p>
    </main>
  );
}
