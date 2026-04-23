export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type StartFormalExamResponse = {
  attempt_id: number;
  assessment_id: number;
  expires_at: string | null;
  status: string;
  exam_session_token: string;
  resume_token: string | null;
};

export type StartMockExamResponse = {
  attempt_id: number;
  assessment_id: number;
  expires_at: string | null;
  status: string;
};

export type EssayReviewItem = {
  review_id: number;
  response_id: number;
  question_id: number;
  attempt_id: number;
  user_id: number | null;
  prompt_md: string;
  student_answer: string;
  proposed_score: number | null;
  confidence: number | null;
  criteria: any[];
  flags: string[];
  rationale: Record<string, any> | null;
  max_marks: number;
};

type ClientOptions = {
  baseUrl: string;
  token?: string;
};

export class BackendClient {
  baseUrl: string;
  token?: string;

  constructor(options: ClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.token = options.token;
  }

  setToken(token: string) {
    this.token = token;
  }

  private headers(extra?: Record<string, string>) {
    return {
      "Content-Type": "application/json",
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...(extra || {}),
    };
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error(`Login failed: ${res.status}`);
    return res.json();
  }

  async startMockExam(assessmentId: number): Promise<StartMockExamResponse> {
    const res = await fetch(`${this.baseUrl}/api/mock-exams/${assessmentId}/start`, {
      method: "POST",
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`Start mock exam failed: ${res.status}`);
    return res.json();
  }

  async startFormalExam(
    assessmentId: number,
    sebConfigHash: string
  ): Promise<StartFormalExamResponse> {
    const res = await fetch(`${this.baseUrl}/api/formal-exams/${assessmentId}/start`, {
      method: "POST",
      headers: this.headers({
        "X-SafeExamBrowser-ConfigKeyHash": sebConfigHash,
      }),
    });
    if (!res.ok) throw new Error(`Start formal exam failed: ${res.status}`);
    return res.json();
  }

  async formalHeartbeat(
    attemptId: number,
    examSessionToken: string,
    nonce?: string
  ) {
    const res = await fetch(`${this.baseUrl}/api/formal-exams/attempts/${attemptId}/heartbeat`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({ exam_session_token: examSessionToken, nonce }),
    });
    if (!res.ok) throw new Error(`Heartbeat failed: ${res.status}`);
    return res.json();
  }

  async getEssayReviewItems(): Promise<{ items: EssayReviewItem[] }> {
    const res = await fetch(`${this.baseUrl}/api/grading/reviews/essay-items`, {
      method: "GET",
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`Essay review fetch failed: ${res.status}`);
    return res.json();
  }
}
