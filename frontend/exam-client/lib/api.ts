const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type TokenResponse = { access_token: string; token_type: string };
type StartFormalExamResponse = {
  attempt_id: number;
  assessment_id: number;
  expires_at: string | null;
  status: string;
  exam_session_token: string;
  resume_token: string | null;
};

export class BackendClient {
  token?: string;
  setToken(token: string) { this.token = token; }
  private headers(extra?: Record<string,string>) {
    return {
      "Content-Type": "application/json",
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...(extra || {}),
    };
  }
  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await fetch(`${API_BASE}/api/auth/login`, { method: "POST", headers: this.headers(), body: JSON.stringify({ email, password }) });
    if (!res.ok) throw new Error(`Login failed: ${res.status}`);
    return res.json();
  }
  async startFormalExam(assessmentId: number, sebConfigHash: string): Promise<StartFormalExamResponse> {
    const res = await fetch(`${API_BASE}/api/formal-exams/${assessmentId}/start`, { method: "POST", headers: this.headers({ "X-SafeExamBrowser-ConfigKeyHash": sebConfigHash }) });
    if (!res.ok) throw new Error(`Start formal exam failed: ${res.status}`);
    return res.json();
  }
  async formalHeartbeat(attemptId: number, examSessionToken: string, nonce?: string) {
    const res = await fetch(`${API_BASE}/api/formal-exams/attempts/${attemptId}/heartbeat`, { method: "POST", headers: this.headers(), body: JSON.stringify({ exam_session_token: examSessionToken, nonce }) });
    if (!res.ok) throw new Error(`Heartbeat failed: ${res.status}`);
    return res.json();
  }
  async fetchPaper(assessmentId: number) {
    const res = await fetch(`${API_BASE}/api/formal-exams/${assessmentId}/paper`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Paper fetch failed: ${res.status}`);
    return res.json();
  }
  async autosave(attemptId: number, examSessionToken: string, responses: any[]) {
    const url = `${API_BASE}/api/formal-exams/attempts/${attemptId}/autosave?exam_session_token=${encodeURIComponent(examSessionToken)}`;
    const res = await fetch(url, { method: "POST", headers: this.headers(), body: JSON.stringify({ responses }) });
    if (!res.ok) throw new Error(`Autosave failed: ${res.status}`);
    return res.json();
  }
  async submit(attemptId: number, examSessionToken: string, submitted_payload: Record<string, any>) {
    const res = await fetch(`${API_BASE}/api/formal-exams/attempts/${attemptId}/submit`, { method: "POST", headers: this.headers(), body: JSON.stringify({ exam_session_token: examSessionToken, submitted_payload }) });
    if (!res.ok) throw new Error(`Submit failed: ${res.status}`);
    return res.json();
  }
}

export const apiBase = API_BASE;
